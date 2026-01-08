# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from contracts.schema import StockData, BacktestMetrics, StrategyConfig, TradeRecord

class BacktestEngine:
    @staticmethod
    def run_backtest(data: StockData) -> BacktestMetrics:
        """
        Runs a vectorized backtest on the provided historical data.
        Strategy: MLStrategy - MACD Crossover (simulating ML signals)
        """
        # Strategy Configuration
        initial_capital = 1000000.0
        commission = 0.002  # 0.2%
        
        config = StrategyConfig(
            strategy_name="MLStrategy",
            initial_capital=initial_capital,
            commission=commission,
            trade_on_close=True,
            position_type="Long-only"
        )
        
        df = pd.DataFrame({
            'Close': data.closes,
            'MACD': data.macd,
            'Signal': data.macd_signal
        }, index=pd.to_datetime(data.dates))
        
        # Generate Signals (Target = 1 for Buy, 0 for Exit)
        df['Target'] = np.where(df['MACD'] > df['Signal'], 1, 0)
        df['Position'] = df['Target'].shift(1).fillna(0)
        df['Returns'] = df['Close'].pct_change()
        df['Strategy_Returns'] = df['Position'] * df['Returns']
        
        # Apply Commission
        df['Position_Change'] = df['Position'].diff().abs()
        df['Commission_Cost'] = df['Position_Change'] * commission
        df['Strategy_Returns'] = df['Strategy_Returns'] - df['Commission_Cost']
        
        # Calculate Equity Curve
        cumulative_returns = (1 + df['Strategy_Returns'].fillna(0)).cumprod()
        equity_curve = (initial_capital * cumulative_returns).tolist()
        final_equity = equity_curve[-1]
        
        # Market Equity (Buy & Hold Benchmark)
        market_returns = df['Returns'].fillna(0)
        market_cumulative = (1 + market_returns).cumprod()
        market_equity = (initial_capital * market_cumulative).tolist()
        
        # --- Time Definitions ---
        days = len(df)
        years = days / 252  # Assuming 252 trading days per year
        
        # --- Strategy Performance Metrics ---
        total_return = (final_equity / initial_capital - 1) * 100
        cagr = ((final_equity / initial_capital) ** (1 / years) - 1) * 100 if years > 0 else 0
        annual_return = cagr  # Same as CAGR
        
        volatility = df['Strategy_Returns'].std() * np.sqrt(252) * 100 if df['Strategy_Returns'].std() != 0 else 0
        
        winning_trades = len(df[df['Strategy_Returns'] > 0])
        total_active_trades = len(df[df['Strategy_Returns'] != 0])
        win_rate = (winning_trades / total_active_trades * 100) if total_active_trades > 0 else 0
        
        peak = (initial_capital * cumulative_returns).expanding(min_periods=1).max()
        drawdown = ((initial_capital * cumulative_returns) / peak - 1) * 100
        drawdown_curve = drawdown.tolist()
        max_drawdown = drawdown.min()
        
        sharpe_ratio = (df['Strategy_Returns'].mean() / df['Strategy_Returns'].std() * np.sqrt(252)) if df['Strategy_Returns'].std() != 0 else 0
        
        avg_trade_return = df[df['Position_Change'] > 0]['Strategy_Returns'].mean() * 100 if len(df[df['Position_Change'] > 0]) > 0 else 0

        # --- Market Metrics ---
        market_total_return = (market_equity[-1] / initial_capital - 1) * 100
        market_annual_return = ((market_equity[-1] / initial_capital) ** (1 / years) - 1) * 100 if years > 0 else 0
        market_volatility = market_returns.std() * np.sqrt(252) * 100 if market_returns.std() != 0 else 0
        market_sharpe_ratio = (market_returns.mean() / market_returns.std() * np.sqrt(252)) if market_returns.std() != 0 else 0
        
        market_peak = (initial_capital * market_cumulative).expanding(min_periods=1).max()
        market_drawdown = ((initial_capital * market_cumulative) / market_peak - 1) * 100
        market_max_drawdown = market_drawdown.min()
        
        # Alpha & Beta
        covariance = np.cov(df['Strategy_Returns'].fillna(0), market_returns)[0][1]
        market_variance = market_returns.var()
        beta = covariance / market_variance if market_variance != 0 else 1.0
        alpha = annual_return - (0 + beta * (market_annual_return - 0)) # CAPM Alpha (Risk Free = 0)
        
        # Information Ratio
        active_returns = df['Strategy_Returns'].fillna(0) - market_returns
        tracking_error = active_returns.std() * np.sqrt(252)
        information_ratio = (active_returns.mean() * 252) / tracking_error if tracking_error != 0 else 0
        
        # Confidence Ratio (Simulated based on MACD strength at entry)
        # We'll normalize the MACD histogram by price to get a relative strength
        df['Signal_Strength'] = (df['MACD'] - df['Signal']).abs() / df['Close']
        confidence_ratio = df[df['Target'] == 1]['Signal_Strength'].mean() * 1000 # Scale up for readability (0-100 range approx)
        if np.isnan(confidence_ratio): confidence_ratio = 50.0 # Default
        
        # Returns list for detailed analysis
        returns_list = df['Strategy_Returns'].fillna(0).tolist()
        
        # Trade History
        trades = []
        buy_signals = []
        sell_signals = []
        
        position_open = False
        entry_idx = 0
        entry_price = 0
        
        for idx in range(len(df)):
            current_signal = df['Target'].iloc[idx]
            
            # Entry: Buy when Target = 1
            if current_signal == 1 and not position_open:
                position_open = True
                entry_idx = idx
                entry_price = df['Close'].iloc[idx]
                buy_signals.append(idx)
            
            # Exit: Close position when Target = 0
            elif current_signal == 0 and position_open:
                position_open = False
                exit_price = df['Close'].iloc[idx]
                profit_loss = (exit_price - entry_price) - (entry_price * commission * 2)  # Entry + Exit commission
                profit_loss_pct = (profit_loss / entry_price) * 100
                duration = idx - entry_idx
                
                trades.append(TradeRecord(
                    entry_date=df.index[entry_idx].strftime('%Y-%m-%d'),
                    exit_date=df.index[idx].strftime('%Y-%m-%d'),
                    entry_price=float(entry_price),
                    exit_price=float(exit_price),
                    profit_loss=float(profit_loss),
                    profit_loss_pct=float(profit_loss_pct),
                    duration_days=int(duration),
                    trade_type="LONG"
                ))
                sell_signals.append(idx)
        
        # Close any open position at the end
        if position_open:
            exit_price = df['Close'].iloc[-1]
            profit_loss = (exit_price - entry_price) - (entry_price * commission * 2)
            profit_loss_pct = (profit_loss / entry_price) * 100
            duration = len(df) - 1 - entry_idx
            
            trades.append(TradeRecord(
                entry_date=df.index[entry_idx].strftime('%Y-%m-%d'),
                exit_date=df.index[-1].strftime('%Y-%m-%d'),
                entry_price=float(entry_price),
                exit_price=float(exit_price),
                profit_loss=float(profit_loss),
                profit_loss_pct=float(profit_loss_pct),
                duration_days=int(duration),
                trade_type="LONG"
            ))
            sell_signals.append(len(df) - 1)
        
        # Monthly Returns
        monthly_returns = df['Strategy_Returns'].resample('ME').sum()
        monthly_returns_dict = {k.strftime('%Y-%m'): float(v) for k, v in monthly_returns.items()}
        
        # Data Scope
        date_range = f"{df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}"
        
        return BacktestMetrics(
            config=config,
            initial_capital=float(initial_capital),
            final_equity=float(final_equity),
            total_trades=len(trades),
            win_rate=float(win_rate),
            max_drawdown=float(max_drawdown),
            total_return=float(total_return),
            annual_return=float(annual_return),
            cagr=float(cagr),
            volatility=float(volatility),
            sharpe_ratio=float(sharpe_ratio),
            avg_trade_return=float(avg_trade_return),
            confidence_ratio=float(confidence_ratio),
            
            # Market Metrics
            market_total_return=float(market_total_return),
            market_annual_return=float(market_annual_return),
            market_volatility=float(market_volatility),
            market_sharpe_ratio=float(market_sharpe_ratio),
            market_max_drawdown=float(market_max_drawdown),
            alpha=float(alpha),
            beta=float(beta),
            information_ratio=float(information_ratio),
            
            entry_rule="Buy when Target = 1 (MACD > Signal)",
            exit_rule="Close position when Target = 0 (MACD < Signal)",
            position_strategy="No short selling implemented",
            equity_curve=equity_curve,
            market_equity=market_equity,
            drawdown_curve=drawdown_curve,
            returns=returns_list,
            dates=data.dates,
            volumes=data.volumes,
            monthly_returns=monthly_returns_dict,
            trades=trades,
            prices=data.closes,
            buy_signals=buy_signals,
            sell_signals=sell_signals,
            data_points=len(df),
            date_range=date_range
        )

