from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.data_loader import load_historical_data
from app.engine import BacktestEngine
from app.schemas import BacktestResponse
from typing import Optional
import os

app = FastAPI(
    title="Backtesting Service",
    description="AI-powered stock trading backtesting API with pipeline integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Backtesting Service",
        "version": "1.0.0",
        "data_sources": ["pipeline", "csv"]
    }


@app.post("/api/v1/backtest/run", response_model=BacktestResponse)
def run_backtest(
    csv_path: str = "ml_trading_signals.csv",
    ticker: Optional[str] = Query(None, description="Stock ticker symbol (e.g., AAPL, MSFT)"),
    use_pipeline: Optional[bool] = Query(None, description="Use pipeline data. If None, uses config setting.")
):
    """
    Run backtesting analysis on historical trading data.
    
    Data Sources:
    - Pipeline (Al-Powered-Stock-ETF-Signal-Generation-Platform-pipeline)
    - CSV file (fallback)
    
    Args:
        csv_path: Path to the CSV file with historical data
        ticker: Optional ticker symbol to load from pipeline
        use_pipeline: Force use of pipeline. If None, uses DATA_SOURCE config.
        
    Returns:
        Comprehensive backtest results including metrics, equity curves, and trade visualization
    
    Examples:
        - Use pipeline: POST /api/v1/backtest/run?ticker=AAPL&use_pipeline=true
        - Use CSV: POST /api/v1/backtest/run?csv_path=data.csv&use_pipeline=false
    """
    try:
        # Check if CSV file exists when not using pipeline
        if use_pipeline is False and not os.path.exists(csv_path):
            raise HTTPException(
                status_code=404,
                detail=f"CSV file not found: {csv_path}"
            )
        
        # Load historical data with pipeline integration
        df = load_historical_data(csv_path=csv_path, ticker=ticker, use_pipeline=use_pipeline)
        
        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="Loaded data is empty"
            )
        
        # Validate required columns
        required_columns = ["Close", "Signal"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {missing_columns}"
            )

        # Initialize backtest engine
        engine = BacktestEngine(df)

        # Run backtests
        market = engine.run_market()
        ml = engine.run_ml()

        # Build visualization data
        equity_curve, pnl_graph, trade_visual = engine.build_graphs(market, ml)

        # Format response
        return BacktestResponse(
            ml_metrics=ml["ml_metrics"],
            market_metrics=market["metrics"],
            trading_metrics=ml["trading_metrics"],
            equity_curve=equity_curve,
            pnl_graph=pnl_graph,
            trade_visualization=trade_visual
        )
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/v1/health")
def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "service": "Backtesting Service"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
