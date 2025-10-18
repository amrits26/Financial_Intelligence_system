"""API Routes for Financial Intelligence System"""
from flask import Blueprint, request, jsonify
from agents.orchestrator import MasterOrchestrator
from utils.validators import validate_stock_symbol, ValidationError
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)
orchestrator = MasterOrchestrator()

@api_bp.route('/analyze', methods=['POST'])
def analyze():
    """Stock analysis endpoint"""
    try:
        data = request.get_json()
        symbol = validate_stock_symbol(data.get('symbol', '').upper())
        period = data.get('period', '1y')

        result = orchestrator.analyze_stock(symbol, period)
        return jsonify(result)

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"API analyze error: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@api_bp.route('/health', methods=['GET'])
def health():
    """System health check"""
    try:
        health_data = orchestrator.get_system_health()
        return jsonify({
            'status': 'healthy',
            'data': health_data
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@api_bp.route('/agents', methods=['GET'])
def agents_status():
    """Get agent status"""
    try:
        health = orchestrator.get_system_health()
        return jsonify(health.get('agents', {}))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
