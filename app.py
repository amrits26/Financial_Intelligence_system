"""Financial Intelligence System - Flask Application"""
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv
from config.settings import Config
from core.database import Database
from core.llm_manager import LLMManager
from agents.orchestrator import MasterOrchestrator
from modules.data_fetcher import DataFetcher
from utils.logging_config import setup_logging
from utils.validators import validate_stock_symbol, ValidationError

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
CORS(app)

logger = setup_logging()
db = Database()
db.initialize()

orchestrator = MasterOrchestrator()
data_fetcher = DataFetcher()


@app.route('/')
def index():
    health = orchestrator.get_system_health()
    recent = db.get_recent_analyses(5)
    return render_template('index.html', health=health, recent=recent)


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    symbol = None
    period = request.values.get('period', '1y')
    result = None

    if request.method == 'POST':
        try:
            symbol = validate_stock_symbol(request.form['symbol'].upper())
            period = request.form.get('period', '1y')
            result = orchestrator.analyze_stock(symbol, period)

            # Always fresh LLM context & summary
            orchestrator.llm_manager = LLMManager()
            result['llm_summary'] = orchestrator._generate_llm_summary(symbol, result)

            db.save_analysis(symbol, result)
            return redirect(url_for('analyze', symbol=symbol, period=period))
        except ValidationError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f"Error: {e}", 'error')

    # GET with query params
    symbol = request.args.get('symbol')
    if symbol:
        try:
            result = orchestrator.analyze_stock(symbol, period)
            orchestrator.llm_manager = LLMManager()
            result['llm_summary'] = orchestrator._generate_llm_summary(symbol, result)
        except Exception as e:
            flash(f"Error loading analysis: {e}", 'error')

    # Build chart_data if analysis exists
        # Build chart_data if analysis exists
        if result and symbol:
            try:
                df = data_fetcher.get_stock_data(symbol, period)
                df = data_fetcher.get_stock_data(symbol, period)
                app.logger.debug(f"Chart DataFrame shape: {df.shape}")
                dates = [d.strftime('%Y-%m-%d') for d in df.index]
                prices = df['close'].tolist()
                sma20 = df['close'].rolling(20).mean().bfill().tolist()
                sma50 = df['close'].rolling(50).mean().bfill().tolist()
                result['chart_data'] = {
                    'dates': dates,
                    'prices': prices,
                    'sma20': sma20,
                    'sma50': sma50
                }
                dates = [d.strftime('%Y-%m-%d') for d in df.index]
                result['chart_data'] = {
                    'dates': dates,
                    'open':  df['open'].tolist(),
                    'high':  df['high'].tolist(),
                    'low':   df['low'].tolist(),
                    'close': df['close'].tolist()
                }
            except Exception as e:
                app.logger.error(f"Error building chart_data: {e}", exc_info=True)



    return render_template('analyze.html', result=result, symbol=symbol, period=period)


@app.route('/portfolio')
def portfolio():
    holdings = db.get_portfolio_holdings()
    metrics = orchestrator.calculate_portfolio_metrics(holdings) if holdings else {}
    return render_template('portfolio.html', holdings=holdings, metrics=metrics)


@app.route('/portfolio/add', methods=['POST'])
def add_portfolio_holding():
    try:
        symbol = validate_stock_symbol(request.form['symbol'].upper())
        quantity = float(request.form['quantity'])
        avg_cost = float(request.form['avg_cost'])
        if quantity <= 0 or avg_cost <= 0:
            flash('Quantity and cost must be positive', 'error')
            return redirect(url_for('portfolio'))

        db.update_portfolio(symbol, quantity, avg_cost)
        flash(f'Added {quantity} shares of {symbol}', 'success')
    except ValidationError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f"Error adding holding: {e}", 'error')

    return redirect(url_for('portfolio'))


@app.route('/portfolio/delete/<symbol>', methods=['POST'])
def delete_portfolio_holding(symbol):
    try:
        db.delete_portfolio_holding(symbol)
        flash(f'Removed {symbol} from portfolio', 'success')
    except Exception as e:
        flash(f"Error removing holding: {e}", 'error')
    return redirect(url_for('portfolio'))


@app.route('/risk')
def risk_dashboard():
    holdings = db.get_portfolio_holdings()
    metrics = orchestrator.assess_portfolio_risk(holdings) if holdings else {}
    return render_template('risk_dashboard.html', metrics=metrics)


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    try:
        data = request.get_json()
        symbol = validate_stock_symbol(data.get('symbol', '').upper())
        period = data.get('period', '1y')
        result = orchestrator.analyze_stock(symbol, period)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/health')
def api_health():
    health = orchestrator.get_system_health()
    return jsonify({'status': 'healthy', 'health': health})


if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
