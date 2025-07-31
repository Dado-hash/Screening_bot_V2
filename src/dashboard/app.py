"""
Streamlit dashboard for cryptocurrency screening with configurable parameters.
Extends existing ScreeningService and configuration system.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, datetime, timedelta
import json
from typing import Dict, List, Any
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.screening_service import ScreeningService
from services.data_service import DataService
from config.settings import ScreeningConfig, get_config
from database.connection import DatabaseTransaction
from repositories.cryptocurrency import CryptocurrencyRepository

# Page configuration
st.set_page_config(
    page_title="Crypto Screening Dashboard V2",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

class ScreeningDashboard:
    """Main dashboard class extending existing services."""
    
    def __init__(self):
        self.config = get_config()
        self.screening_service = ScreeningService()
        self.data_service = DataService()
        
    def run(self):
        """Main dashboard runner."""
        st.title("🚀 Crypto Screening Dashboard V2")
        st.markdown("**Parametri configurabili in tempo reale | Database SQLite | Performance ottimizzate**")
        
        # Sidebar for configuration
        self.render_sidebar()
        
        # Main content tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Data Management", "🎯 Screening", "📈 Visualizations", "⚙️ Configuration", "📋 Results"])
        
        with tab1:
            self.render_data_management_tab()
        
        with tab2:
            self.render_screening_tab()
        
        with tab3:
            self.render_visualizations_tab()
            
        with tab4:
            self.render_configuration_tab()
            
        with tab5:
            self.render_results_tab()
    
    def render_sidebar(self):
        """Render configuration sidebar extending existing ScreeningConfig."""
        st.sidebar.header("🔧 Configuration Parameters")
        
        # Initialize session state
        if 'config_params' not in st.session_state:
            st.session_state.config_params = {
                'sma_fast': self.config.screening.sma_fast,
                'sma_medium': self.config.screening.sma_medium,
                'sma_slow': self.config.screening.sma_slow,
                'rank_scores': self.config.screening.rank_scores.copy(),
                'sma_scores': self.config.screening.sma_scores.copy(),
                'min_volume_threshold': self.config.screening.min_volume_threshold,
                'max_coins_per_analysis': self.config.screening.max_coins_per_analysis
            }
        
        # SMA Periods Configuration
        st.sidebar.subheader("📊 SMA Periods")
        st.session_state.config_params['sma_fast'] = st.sidebar.slider(
            "Fast SMA", 3, 15, st.session_state.config_params['sma_fast'], 
            help="Periodo SMA veloce (default: 6)"
        )
        st.session_state.config_params['sma_medium'] = st.sidebar.slider(
            "Medium SMA", 8, 25, st.session_state.config_params['sma_medium'],
            help="Periodo SMA medio (default: 11)"
        )
        st.session_state.config_params['sma_slow'] = st.sidebar.slider(
            "Slow SMA", 15, 50, st.session_state.config_params['sma_slow'],
            help="Periodo SMA lento (default: 21)"
        )
        
        # Rank Scores Configuration
        st.sidebar.subheader("🏆 Rank Scores")
        st.session_state.config_params['rank_scores']['top_10'] = st.sidebar.number_input(
            "Top 10 Score", 0, 10, st.session_state.config_params['rank_scores']['top_10']
        )
        st.session_state.config_params['rank_scores']['top_15'] = st.sidebar.number_input(
            "Top 15 Score", 0, 10, st.session_state.config_params['rank_scores']['top_15']
        )
        st.session_state.config_params['rank_scores']['top_20'] = st.sidebar.number_input(
            "Top 20 Score", 0, 10, st.session_state.config_params['rank_scores']['top_20']
        )
        
        # SMA Scores Configuration
        st.sidebar.subheader("📈 SMA Scores")
        st.session_state.config_params['sma_scores']['above_fast'] = st.sidebar.number_input(
            "Above Fast SMA", -5, 5, st.session_state.config_params['sma_scores']['above_fast']
        )
        st.session_state.config_params['sma_scores']['above_medium'] = st.sidebar.number_input(
            "Above Medium SMA", -5, 5, st.session_state.config_params['sma_scores']['above_medium']
        )
        st.session_state.config_params['sma_scores']['above_slow'] = st.sidebar.number_input(
            "Above Slow SMA", -5, 5, st.session_state.config_params['sma_scores']['above_slow']
        )
        
        # Filters
        st.sidebar.subheader("🔍 Filters")
        st.session_state.config_params['min_volume_threshold'] = st.sidebar.number_input(
            "Min Volume (USD)", 0.0, 100000.0, st.session_state.config_params['min_volume_threshold'],
            step=1000.0
        )
        st.session_state.config_params['max_coins_per_analysis'] = st.sidebar.number_input(
            "Max Coins", 10, 500, st.session_state.config_params['max_coins_per_analysis']
        )
        
        # Apply Configuration Button
        if st.sidebar.button("✅ Apply Configuration"):
            self.update_screening_config()
            st.sidebar.success("Configuration updated!")
    
    def update_screening_config(self):
        """Update ScreeningService configuration with user parameters."""
        # Create new config with user parameters
        new_config = ScreeningConfig(
            sma_fast=st.session_state.config_params['sma_fast'],
            sma_medium=st.session_state.config_params['sma_medium'],
            sma_slow=st.session_state.config_params['sma_slow'],
            rank_scores=st.session_state.config_params['rank_scores'],
            sma_scores=st.session_state.config_params['sma_scores'],
            min_volume_threshold=st.session_state.config_params['min_volume_threshold'],
            max_coins_per_analysis=st.session_state.config_params['max_coins_per_analysis']
        )
        
        # Update screening service
        self.screening_service.config = new_config
    
    def render_data_management_tab(self):
        """Render data management interface for populating database."""
        st.header("📊 Data Management")
        st.markdown("**Popola il database con coin da diverse fonti dati**")
        
        # Current database status
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Database Status")
            try:
                stats = self.data_service.get_data_coverage_stats()
                st.metric("Total Cryptocurrencies", stats.get('total_cryptocurrencies', 0))
                st.metric("Active Cryptocurrencies", stats.get('active_cryptocurrencies', 0))
                st.metric("Price Records", stats.get('total_price_records', 0))
                st.metric("SMA Records", stats.get('total_sma_records', 0))
            except Exception as e:
                st.error(f"Error loading database stats: {e}")
        
        with col2:
            st.subheader("🔌 Available Data Sources")
            try:
                sources = self.data_service.get_available_data_sources()
                
                for source_name, source_info in sources.items():
                    status = "✅ Available" if source_info['available'] else "❌ Not configured"
                    st.write(f"**{source_name.title()}**: {status}")
                    
                    # Show API key status for CoinGecko
                    if source_name == 'coingecko':
                        api_key_status = "🔑 With API Key" if source_info.get('has_api_key') else "🆓 Free (rate limited)"
                        st.write(f"  - Status: {api_key_status}")
                    
                    st.write(f"  - {source_info['description']}")
                    st.write(f"  - Max coins: {source_info['max_coins']}")
                    st.write("")
            except Exception as e:
                st.error(f"Error loading data sources: {e}")
        
        st.divider()
        
        # Data fetching section
        st.subheader("🚀 Fetch New Cryptocurrency Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🥇 CoinGecko - Top by Market Cap")
            
            number_coins = st.number_input(
                "Number of top coins to fetch",
                min_value=10,
                max_value=1000,
                value=100,
                step=10,
                help="Fetch top cryptocurrencies by market capitalization"
            )
            
            if st.button("🔄 Fetch from CoinGecko", type="primary"):
                self.fetch_coingecko_data(number_coins)
        
        with col2:
            st.markdown("### ⚡ Binance - All BTC Pairs")
            
            st.info("Fetches all active BTC trading pairs from Binance exchange")
            
            if st.button("🔄 Fetch from Binance"):
                self.fetch_binance_data()
        
        st.divider()
        
        # Historical data fetching
        st.subheader("📅 Fetch Historical Price Data")
        
        available_coins = self.get_available_coins()
        
        if available_coins:
            selected_coins_for_history = st.multiselect(
                "Select coins for historical data fetch",
                options=available_coins,
                default=available_coins[:min(20, len(available_coins))],
                help="Select coins to fetch historical price data"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                history_days = st.number_input(
                    "Days of historical data",
                    min_value=7,
                    max_value=365,
                    value=30,
                    help="Number of days of historical data to fetch"
                )
            
            with col2:
                if st.button("📊 Fetch Historical Data", disabled=not selected_coins_for_history):
                    if selected_coins_for_history:
                        self.fetch_historical_data(selected_coins_for_history, history_days)
        else:
            st.warning("No coins available. Please fetch coins from CoinGecko or Binance first.")
        
        st.divider()
        
        # API Keys configuration info
        st.subheader("🔑 API Keys Configuration")
        
        st.info(
            """
            **Per ottimizzare le performance:**
            
            **CoinGecko** (Raccomandato):
            - ✅ Funziona già senza API key (rate limited)
            - 🚀 Con API key: rate limits più alti
            - 📝 Registrati gratis su: https://www.coingecko.com/en/api
            
            **Binance** (Opzionale):
            - 🔐 Richiede API key per accesso
            - 📝 Crea API key su: https://www.binance.com/en/my/settings/api-management
            
            **Come configurare:**
            1. Modifica il file `config/api_keys.py`
            2. Inserisci le tue API keys
            3. Riavvia la dashboard
            """
        )
        
        # Show current API configuration
        with st.expander("🔍 Current API Configuration"):
            try:
                from config.settings import get_api_config
                api_config = get_api_config()
                
                coingecko_configured = bool(api_config.coingecko_api_key and 
                                          api_config.coingecko_api_key != "your_coingecko_api_key_here")
                binance_configured = bool(api_config.binance_api_key and api_config.binance_secret_key and
                                        api_config.binance_api_key != "your_binance_api_key_here")
                
                st.write(f"**CoinGecko API Key**: {'✅ Configured' if coingecko_configured else '❌ Not configured (using free access)'}")
                st.write(f"**Binance API Key**: {'✅ Configured' if binance_configured else '❌ Not configured'}")
                
            except Exception as e:
                st.error(f"Error checking API configuration: {e}")
    
    def fetch_coingecko_data(self, number_coins: int):
        """Fetch cryptocurrency data from CoinGecko."""
        with st.spinner(f"🔄 Fetching top {number_coins} coins from CoinGecko..."):
            try:
                import asyncio
                
                # Run async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.data_service.populate_coins_from_coingecko(number_coins)
                )
                loop.close()
                
                if result.get('success'):
                    st.success(f"✅ CoinGecko fetch completed!")
                    st.write(f"- Added: {result.get('added', 0)} new coins")
                    st.write(f"- Updated: {result.get('updated', 0)} existing coins")
                    st.write(f"- Total: {result.get('total', 0)} coins processed")
                    
                    # Refresh the page to show updated stats
                    st.rerun()
                else:
                    st.error(f"❌ CoinGecko fetch failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"Error fetching CoinGecko data: {e}")
    
    def fetch_binance_data(self):
        """Fetch cryptocurrency data from Binance."""
        with st.spinner("🔄 Fetching BTC pairs from Binance..."):
            try:
                result = self.data_service.populate_coins_from_binance()
                
                if result.get('success'):
                    st.success(f"✅ Binance fetch completed!")
                    st.write(f"- Added: {result.get('added', 0)} new coins")
                    st.write(f"- Updated: {result.get('updated', 0)} existing coins")
                    st.write(f"- Total: {result.get('total', 0)} coins processed")
                    
                    # Refresh the page to show updated stats
                    st.rerun()
                else:
                    st.error(f"❌ Binance fetch failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"Error fetching Binance data: {e}")
    
    def fetch_historical_data(self, coin_ids: List[str], days: int):
        """Fetch historical data for selected coins."""
        with st.spinner(f"📊 Fetching {days} days of historical data for {len(coin_ids)} coins..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                import asyncio
                
                status_text.text("Initializing data fetch...")
                progress_bar.progress(10)
                
                # Run async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                status_text.text("Fetching data from CoinGecko...")
                progress_bar.progress(50)
                
                result = loop.run_until_complete(
                    self.data_service.fetch_and_store_historical_data(coin_ids, days)
                )
                loop.close()
                
                progress_bar.progress(90)
                status_text.text("Processing and storing data...")
                
                if result.get('success'):
                    progress_bar.progress(100)
                    status_text.text("✅ Historical data fetch completed!")
                    
                    st.success(f"✅ Historical data fetch completed!")
                    st.write(f"- Processed: {result.get('processed', 0)} coins")
                    st.write(f"- Errors: {result.get('errors', 0)} coins")
                    st.write(f"- Total requested: {result.get('total_coins', 0)} coins")
                    
                    if result.get('errors', 0) > 0:
                        st.warning(f"⚠️ {result.get('errors')} coins had errors during fetch")
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                else:
                    st.error(f"❌ Historical data fetch failed: {result.get('error', 'Unknown error')}")
                    progress_bar.empty()
                    status_text.empty()
                    
            except Exception as e:
                st.error(f"Error fetching historical data: {e}")
                progress_bar.empty()
                status_text.empty()
    
    def render_screening_tab(self):
        """Render main screening interface using existing ScreeningService."""
        st.header("🎯 Interactive Cryptocurrency Screening")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Get available coins from database
            available_coins = self.get_available_coins()
            selected_coins = st.multiselect(
                "Select Cryptocurrencies",
                options=available_coins,
                default=available_coins[:10] if len(available_coins) >= 10 else available_coins,
                help="Select coins to analyze"
            )
        
        with col2:
            analysis_date = st.date_input(
                "Analysis Date",
                value=date.today() - timedelta(days=7),
                help="Date for analysis"
            )
        
        with col3:
            direction = st.selectbox(
                "Direction",
                options=["forward", "backward"],
                help="Analysis direction"
            )
        
        # Timeframes selection
        st.subheader("📅 Timeframes")
        default_timeframes = [1, 3, 7, 14, 20]
        timeframes = st.multiselect(
            "Select timeframes (days)",
            options=list(range(1, 31)),
            default=default_timeframes,
            help="Select analysis timeframes"
        )
        
        # Run screening button
        if st.button("🚀 Run Screening Analysis", type="primary", disabled=not selected_coins):
            if selected_coins and timeframes:
                self.run_screening_analysis(selected_coins, analysis_date, direction, timeframes)
            else:
                st.warning("Please select at least one coin and one timeframe.")
    
    def get_available_coins(self) -> List[str]:
        """Get available coins from database using existing repository."""
        try:
            with DatabaseTransaction() as session:
                crypto_repo = CryptocurrencyRepository(session)
                cryptos = crypto_repo.get_all()
                return [crypto.coin_id for crypto in cryptos]
        except Exception as e:
            st.error(f"Error fetching coins: {e}")
            return []
    
    def run_screening_analysis(self, coin_ids: List[str], analysis_date: date, 
                              direction: str, timeframes: List[int]):
        """Run screening analysis using existing ScreeningService."""
        
        with st.spinner("🔄 Running screening analysis..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Update progress
                progress_bar.progress(25)
                status_text.text("Fetching data from database...")
                
                # Run analysis using existing service
                results = self.screening_service.run_comprehensive_screening(
                    coin_ids=coin_ids,
                    analysis_date=analysis_date,
                    direction=direction,
                    timeframes=timeframes
                )
                
                progress_bar.progress(75)
                status_text.text("Processing results...")
                
                # Store results in session state
                st.session_state.screening_results = results
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis completed!")
                
                # Display results
                self.display_screening_results(results)
                
            except Exception as e:
                st.error(f"Error running analysis: {e}")
                progress_bar.empty()
                status_text.empty()
    
    def display_screening_results(self, results: Dict[str, Any]):
        """Display screening results with interactive elements."""
        
        st.success(f"✅ Analysis completed! {results['total_coins']} coins analyzed.")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Coins", results['total_coins'])
        
        with col2:
            st.metric("Timeframes", len(results['timeframes']))
        
        with col3:
            total_analyses = results.get('statistics', {}).get('total_analyses', 0)
            st.metric("Total Analyses", total_analyses)
        
        with col4:
            st.metric("Direction", results['direction'].title())
        
        # Leaderboard
        if results.get('leaderboard'):
            st.subheader("🏆 Final Leaderboard")
            
            leaderboard_df = pd.DataFrame(results['leaderboard'])
            
            # Format columns for display
            display_columns = ['final_rank', 'coin_id', 'total_score', 'avg_score', 'avg_return', 'best_rank']
            if all(col in leaderboard_df.columns for col in display_columns):
                display_df = leaderboard_df[display_columns].copy()
                display_df.columns = ['Rank', 'Coin', 'Total Score', 'Avg Score', 'Avg Return %', 'Best Rank']
                display_df['Avg Return %'] = display_df['Avg Return %'].round(2)
                display_df['Avg Score'] = display_df['Avg Score'].round(1)
                
                st.dataframe(display_df, use_container_width=True)
            
            # Daily Evolution Table (like your Excel cumulative_changes)
            self.render_daily_evolution_table(results)
            
            # Export functionality
            self.render_export_section(results)
    
    def render_export_section(self, results: Dict[str, Any]):
        """Render export functionality using existing export methods."""
        st.subheader("📥 Export Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export to Excel"):
                try:
                    output_path = f"data/outputs/dashboard_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    success = self.screening_service.export_results_to_excel(results, output_path)
                    if success:
                        st.success(f"Results exported to {output_path}")
                    else:
                        st.error("Export failed")
                except Exception as e:
                    st.error(f"Export error: {e}")
    
    def render_daily_evolution_table(self, results: Dict[str, Any]):
        """Render daily evolution table like the Excel cumulative_changes."""
        st.subheader("📊 Daily Evolution - Cumulative Changes (Like Excel)")
        
        if not results.get('leaderboard'):
            st.warning("No leaderboard data available for daily evolution.")
            return
        
        # Extract timeframe data from leaderboard
        leaderboard = results.get('leaderboard', [])
        timeframes = results.get('timeframes', [])
        
        if not timeframes:
            st.warning("No timeframes data available.")
            return
        
        # Create evolution dataframe
        evolution_data = []
        
        for coin_data in leaderboard:
            coin_id = coin_data['coin_id']
            timeframe_scores = coin_data.get('timeframe_scores', {})
            timeframe_returns = coin_data.get('timeframe_returns', {})
            
            # Create row for this coin
            row = {'Coin': coin_id}
            
            # Add scores for each timeframe (day)
            for tf in sorted(timeframes):
                if tf in timeframe_scores:
                    score = timeframe_scores[tf]
                    return_pct = timeframe_returns.get(tf, 0)
                    # Show score and return percentage
                    row[f'{tf}d Score'] = score
                    row[f'{tf}d Return%'] = round(return_pct, 2)
                else:
                    row[f'{tf}d Score'] = 0
                    row[f'{tf}d Return%'] = 0.0
            
            # Add total score
            row['Total Score'] = coin_data.get('total_score', 0)
            row['Final Rank'] = coin_data.get('final_rank', 0)
            
            evolution_data.append(row)
        
        if evolution_data:
            evolution_df = pd.DataFrame(evolution_data)
            
            # Sort by Total Score (descending)
            evolution_df = evolution_df.sort_values('Total Score', ascending=False)
            
            st.write(f"**Evolution table for {len(evolution_df)} coins across {len(timeframes)} timeframes**")
            
            # Style the dataframe
            styled_df = evolution_df.style.format({
                col: '{:.1f}' for col in evolution_df.columns if 'Score' in col
            }).format({
                col: '{:.2f}%' for col in evolution_df.columns if 'Return%' in col
            }).background_gradient(subset=[col for col in evolution_df.columns if 'Score' in col], cmap='RdYlGn')
            
            st.dataframe(styled_df, use_container_width=True)
            
            # Interactive filters
            with st.expander("🔍 Filter & Analysis Tools"):
                col1, col2 = st.columns(2)
                
                with col1:
                    min_total_score = st.number_input(
                        "Minimum Total Score",
                        value=0,
                        step=1,
                        help="Filter coins with total score above this value"
                    )
                
                with col2:
                    top_n_coins = st.number_input(
                        "Show Top N Coins",
                        value=min(10, len(evolution_df)),
                        min_value=1,
                        max_value=len(evolution_df),
                        help="Show only top N performing coins"
                    )
                
                # Apply filters
                filtered_df = evolution_df[evolution_df['Total Score'] >= min_total_score].head(top_n_coins)
                
                if not filtered_df.empty:
                    st.write(f"**Filtered Results: {len(filtered_df)} coins**")
                    
                    # Create summary stats
                    st.write("**Performance Summary:**")
                    summary_cols = st.columns(4)
                    
                    with summary_cols[0]:
                        avg_total_score = filtered_df['Total Score'].mean()
                        st.metric("Avg Total Score", f"{avg_total_score:.1f}")
                    
                    with summary_cols[1]:
                        best_coin = filtered_df.iloc[0]['Coin'] if not filtered_df.empty else "N/A"
                        st.metric("Best Coin", best_coin)
                    
                    with summary_cols[2]:
                        max_score = filtered_df['Total Score'].max()
                        st.metric("Max Score", f"{max_score:.1f}")
                    
                    with summary_cols[3]:
                        score_std = filtered_df['Total Score'].std()
                        st.metric("Score Std Dev", f"{score_std:.1f}")
                    
                    # Show filtered table
                    st.dataframe(
                        filtered_df.style.format({
                            col: '{:.1f}' for col in filtered_df.columns if 'Score' in col
                        }).format({
                            col: '{:.2f}%' for col in filtered_df.columns if 'Return%' in col
                        }).background_gradient(
                            subset=[col for col in filtered_df.columns if 'Score' in col], 
                            cmap='RdYlGn'
                        ),
                        use_container_width=True
                    )
        else:
            st.warning("No evolution data available to display.")
        
        with col2:
            if st.button("📋 Download JSON"):
                json_data = json.dumps(results, indent=2, default=str)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"screening_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col3:
            if st.button("📄 Download CSV"):
                if results.get('leaderboard'):
                    csv_data = pd.DataFrame(results['leaderboard']).to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"leaderboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
    
    def render_visualizations_tab(self):
        """Render interactive visualizations using Plotly."""
        st.header("📊 Interactive Visualizations")
        
        if 'screening_results' not in st.session_state:
            st.info("Run a screening analysis first to see visualizations.")
            return
        
        results = st.session_state.screening_results
        
        if not results.get('leaderboard'):
            st.warning("No data available for visualization.")
            return
        
        # Create visualizations
        self.create_performance_chart(results)
        self.create_score_distribution(results)
        self.create_timeframe_heatmap(results)
    
    def create_performance_chart(self, results: Dict[str, Any]):
        """Create performance chart using Plotly."""
        st.subheader("📈 Performance Chart")
        
        leaderboard_df = pd.DataFrame(results['leaderboard'])
        
        if 'total_score' in leaderboard_df.columns and 'avg_return' in leaderboard_df.columns:
            fig = px.scatter(
                leaderboard_df,
                x='avg_return',
                y='total_score',
                hover_data=['coin_id', 'final_rank'],
                title="Total Score vs Average Return",
                labels={'avg_return': 'Average Return (%)', 'total_score': 'Total Score'}
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    def create_score_distribution(self, results: Dict[str, Any]):
        """Create score distribution histogram."""
        st.subheader("📊 Score Distribution")
        
        leaderboard_df = pd.DataFrame(results['leaderboard'])
        
        if 'total_score' in leaderboard_df.columns:
            fig = px.histogram(
                leaderboard_df,
                x='total_score',
                nbins=20,
                title="Distribution of Total Scores"
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    def create_timeframe_heatmap(self, results: Dict[str, Any]):
        """Create timeframe performance heatmap."""
        st.subheader("🔥 Timeframe Performance Heatmap")
        
        leaderboard = results.get('leaderboard', [])
        
        if not leaderboard:
            st.warning("No timeframe data available.")
            return
        
        # Prepare data for heatmap
        heatmap_data = []
        for coin_data in leaderboard[:20]:  # Top 20 coins
            coin_id = coin_data['coin_id']
            timeframe_scores = coin_data.get('timeframe_scores', {})
            timeframe_returns = coin_data.get('timeframe_returns', {})
            
            for timeframe in sorted(timeframe_scores.keys()):
                heatmap_data.append({
                    'Coin': coin_id,
                    'Timeframe': f"{timeframe}d",
                    'Score': timeframe_scores[timeframe],
                    'Return': timeframe_returns.get(timeframe, 0)
                })
        
        if heatmap_data:
            heatmap_df = pd.DataFrame(heatmap_data)
            pivot_scores = heatmap_df.pivot(index='Coin', columns='Timeframe', values='Score')
            
            fig = px.imshow(
                pivot_scores.values,
                x=pivot_scores.columns,
                y=pivot_scores.index,
                aspect='auto',
                title="Score Heatmap by Coin and Timeframe"
            )
            
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
    
    def render_configuration_tab(self):
        """Render detailed configuration management."""
        st.header("⚙️ Advanced Configuration")
        
        # Current configuration display
        st.subheader("📋 Current Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.json({
                "SMA Periods": {
                    "Fast": st.session_state.config_params['sma_fast'],
                    "Medium": st.session_state.config_params['sma_medium'],
                    "Slow": st.session_state.config_params['sma_slow']
                },
                "Rank Scores": st.session_state.config_params['rank_scores']
            })
        
        with col2:
            st.json({
                "SMA Scores": st.session_state.config_params['sma_scores'],
                "Filters": {
                    "Min Volume": st.session_state.config_params['min_volume_threshold'],
                    "Max Coins": st.session_state.config_params['max_coins_per_analysis']
                }
            })
        
        # Configuration presets
        st.subheader("🎛️ Configuration Presets")
        
        presets = {
            "Conservative": {
                "rank_scores": {"top_10": 2, "top_15": 1, "top_20": 1, "other": 0},
                "sma_scores": {"above_fast": 1, "above_medium": 1, "above_slow": 2, "below_fast": -1, "below_medium": -1, "below_slow": -2}
            },
            "Aggressive": {
                "rank_scores": {"top_10": 5, "top_15": 3, "top_20": 1, "other": 0},
                "sma_scores": {"above_fast": 2, "above_medium": 3, "above_slow": 4, "below_fast": -2, "below_medium": -3, "below_slow": -4}
            },
            "Balanced": {
                "rank_scores": {"top_10": 3, "top_15": 2, "top_20": 1, "other": 0},
                "sma_scores": {"above_fast": 1, "above_medium": 2, "above_slow": 3, "below_fast": -1, "below_medium": -2, "below_slow": -3}
            }
        }
        
        selected_preset = st.selectbox("Choose Preset", list(presets.keys()))
        
        if st.button("Apply Preset"):
            preset_config = presets[selected_preset]
            st.session_state.config_params['rank_scores'].update(preset_config['rank_scores'])
            st.session_state.config_params['sma_scores'].update(preset_config['sma_scores'])
            st.success(f"{selected_preset} preset applied!")
            st.rerun()
    
    def render_results_tab(self):
        """Render detailed results analysis."""
        st.header("📈 Detailed Results Analysis")
        
        if 'screening_results' not in st.session_state:
            st.info("Run a screening analysis first to see detailed results.")
            return
        
        results = st.session_state.screening_results
        
        # Statistics
        if 'statistics' in results:
            st.subheader("📊 Analysis Statistics")
            stats = results['statistics']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Score Statistics**")
                if 'score_stats' in stats:
                    score_stats = stats['score_stats']
                    st.write(f"- Mean: {score_stats.get('mean', 0):.2f}")
                    st.write(f"- Std Dev: {score_stats.get('std', 0):.2f}")
                    st.write(f"- Min: {score_stats.get('min', 0):.2f}")
                    st.write(f"- Max: {score_stats.get('max', 0):.2f}")
                    st.write(f"- Median: {score_stats.get('median', 0):.2f}")
            
            with col2:
                st.write("**Return Statistics**")
                if 'return_stats' in stats:
                    return_stats = stats['return_stats']
                    st.write(f"- Mean: {return_stats.get('mean', 0):.2f}%")
                    st.write(f"- Std Dev: {return_stats.get('std', 0):.2f}%")
                    st.write(f"- Min: {return_stats.get('min', 0):.2f}%")
                    st.write(f"- Max: {return_stats.get('max', 0):.2f}%")
                    st.write(f"- Median: {return_stats.get('median', 0):.2f}%")
        
        # Detailed leaderboard
        if results.get('leaderboard'):
            st.subheader("🔍 Detailed Leaderboard")
            
            leaderboard_df = pd.DataFrame(results['leaderboard'])
            
            # Add filters
            col1, col2 = st.columns(2)
            
            with col1:
                min_score = st.number_input("Minimum Total Score", value=0)
            
            with col2:
                min_return = st.number_input("Minimum Avg Return %", value=-100.0)
            
            # Filter data
            filtered_df = leaderboard_df[
                (leaderboard_df['total_score'] >= min_score) &
                (leaderboard_df['avg_return'] >= min_return)
            ]
            
            st.dataframe(filtered_df, use_container_width=True)


def main():
    """Main application entry point."""
    dashboard = ScreeningDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()