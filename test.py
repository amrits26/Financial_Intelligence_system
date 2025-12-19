from main import run_financial_analysis

if __name__ == "__main__":
    ticker_symbol = input("Enter a nyse ticker: ")  # Try AMZN, GOOG, TSLA, AAPL, ORCL, MSFT, etc
    print("\n")
    
    try:
        result = run_financial_analysis(ticker_symbol)
        
        print("\n--- EXECUTIVE SUMMARY ---")
        
        # Check if analysis was successful
        if result.get("success", True):
            print(result.get('final_report', 'No report available'))
        else:
            error_msg = result.get("error", "Unknown error occurred")
            print(f"❌ Analysis failed: {error_msg}")
            print(f"\nPlease verify the ticker symbol '{ticker_symbol}' is correct and try again.")
            print("Valid examples: AAPL, MSFT, GOOGL, TSLA, AMZN, NVDA")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("Please check your input and try again.")