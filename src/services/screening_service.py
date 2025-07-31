"""Modern screening service with database integration and optimized algorithms."""

from datetime import date, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np

from loguru import logger

from database.connection import DatabaseTransaction
from repositories import (
    CryptocurrencyRepository,
    HistoricalPriceRepository, 
    SMAIndicatorRepository,
    ScreeningResultRepository,
    CacheRepository
)
from config.settings import get_screening_config, ScreeningConfig


class ScreeningService:
    """Modern cryptocurrency screening service."""
    
    def __init__(self, config: Optional[ScreeningConfig] = None):
        self.config = config or get_screening_config()
        self.cache_ttl = 7200  # 2 hours for analysis results
    
    def run_comprehensive_screening(self, coin_ids: List[str], analysis_date: date, 
                                  direction: str = 'forward', timeframes: List[int] = None) -> Dict[str, Any]:
        """Run comprehensive screening analysis for given cryptocurrencies."""
        
        if timeframes is None:
            timeframes = self.config.cumulative_periods[:10]  # First 10 days
        
        logger.info(f"Starting comprehensive screening for {len(coin_ids)} coins, direction: {direction}")
        
        cache_key = f"screening_{hash(str(sorted(coin_ids)))}_{analysis_date}_{direction}_{hash(str(timeframes))}"
        
        with DatabaseTransaction() as session:
            cache_repo = CacheRepository(session)
            
            # Try cache first
            cached_result = cache_repo.get_cached_value(cache_key)
            if cached_result:
                logger.debug("Using cached screening results")
                return cached_result
            
            # Run fresh analysis
            results = self._run_screening_analysis(session, coin_ids, analysis_date, direction, timeframes)
            
            # Cache the results
            cache_repo.set_cached_value(cache_key, results, self.cache_ttl, 'screening_results')
            
            logger.info(f"Comprehensive screening completed for {len(results.get('leaderboard', []))} coins")
            return results
    
    def _run_screening_analysis(self, session, coin_ids: List[str], analysis_date: date, 
                               direction: str, timeframes: List[int]) -> Dict[str, Any]:
        """Internal method to run the screening analysis."""
        
        crypto_repo = CryptocurrencyRepository(session)
        price_repo = HistoricalPriceRepository(session)
        sma_repo = SMAIndicatorRepository(session)
        result_repo = ScreeningResultRepository(session)
        
        # Get cryptocurrency objects
        cryptos = crypto_repo.get_by_coin_ids(coin_ids)
        crypto_map = {crypto.coin_id: crypto for crypto in cryptos}
        
        if not cryptos:
            logger.warning("No cryptocurrencies found in database")
            return {'leaderboard': [], 'statistics': {}}
        
        # Calculate date range based on direction
        if direction == 'forward':
            start_date = analysis_date
            end_date = analysis_date + timedelta(days=max(timeframes) + 5)
        else:  # backward
            end_date = analysis_date
            start_date = analysis_date - timedelta(days=max(timeframes) + 5)
        
        # Get price data as DataFrame
        logger.debug(f"Fetching price data from {start_date} to {end_date}")
        price_df = price_repo.get_price_history_dataframe(coin_ids, max(timeframes) + 10, 'price_btc')
        
        if price_df.empty:
            logger.warning("No price data available for analysis")
            return {'leaderboard': [], 'statistics': {}}
        
        # Get SMA data
        sma_data = self._get_sma_dataframes(sma_repo, coin_ids, max(timeframes) + 10)
        
        # Calculate cumulative returns for all timeframes
        cumulative_returns = self._calculate_cumulative_returns(price_df, timeframes, direction, analysis_date)
        
        # Calculate scores for each timeframe
        screening_results = []
        
        for timeframe in timeframes:
            if timeframe not in cumulative_returns:
                continue
                
            timeframe_results = self._analyze_timeframe(
                cumulative_returns[timeframe], 
                sma_data, 
                timeframe, 
                analysis_date,
                direction
            )
            
            # Store results in database
            for result in timeframe_results:
                coin_id = result['coin_id']
                if coin_id in crypto_map:
                    crypto = crypto_map[coin_id]
                    
                    result_repo.create_or_update_result(
                        cryptocurrency_id=crypto.id,
                        analysis_date=analysis_date,
                        timeframe_days=timeframe,
                        direction=direction,
                        cumulative_return=result['cumulative_return'],
                        rank_position=result['rank_position'],
                        rank_change=result.get('rank_change', 0),
                        day_rank_score=result['day_rank_score'],
                        sma_fast_score=result['sma_fast_score'],
                        sma_medium_score=result['sma_medium_score'],
                        sma_slow_score=result['sma_slow_score'],
                        total_score=result['total_score']
                    )
            
            screening_results.extend(timeframe_results)
        
        # Create final leaderboard
        leaderboard = self._create_final_leaderboard(screening_results, timeframes)
        
        # Calculate statistics
        statistics = self._calculate_statistics(screening_results)
        
        return {
            'leaderboard': leaderboard,
            'statistics': statistics,
            'analysis_date': analysis_date.isoformat(),
            'direction': direction,
            'timeframes': timeframes,
            'total_coins': len(coin_ids)
        }
    
    def _get_sma_dataframes(self, sma_repo: SMAIndicatorRepository, coin_ids: List[str], 
                          days: int) -> Dict[str, pd.DataFrame]:
        """Get SMA dataframes for all periods."""
        return {
            'above_sma_6': sma_repo.get_above_sma_dataframe(coin_ids, days, 'above_sma_6'),
            'above_sma_11': sma_repo.get_above_sma_dataframe(coin_ids, days, 'above_sma_11'),  
            'above_sma_21': sma_repo.get_above_sma_dataframe(coin_ids, days, 'above_sma_21')
        }
    
    def _calculate_cumulative_returns(self, price_df: pd.DataFrame, timeframes: List[int], 
                                    direction: str, analysis_date: date) -> Dict[int, pd.Series]:
        """Calculate cumulative returns for all timeframes using vectorized operations."""
        
        if price_df.empty:
            return {}
        
        # Ensure data is sorted by date
        price_df = price_df.sort_index()
        
        cumulative_returns = {}
        
        try:
            for timeframe in timeframes:
                if direction == 'backward':
                    # From today going back
                    if len(price_df) > timeframe:
                        end_prices = price_df.iloc[-1]  # Most recent
                        start_prices = price_df.iloc[-(timeframe + 1)]  # N days ago
                        
                        # Vectorized calculation
                        returns = ((end_prices - start_prices) / start_prices * 100).dropna()
                        cumulative_returns[timeframe] = returns.sort_values(ascending=False)
                
                else:  # forward
                    # From analysis_date going forward
                    try:
                        # Find the closest date to analysis_date
                        analysis_idx = price_df.index.get_indexer([analysis_date], method='nearest')[0]
                        
                        if analysis_idx >= 0 and analysis_idx + timeframe < len(price_df):
                            start_prices = price_df.iloc[analysis_idx]
                            end_prices = price_df.iloc[analysis_idx + timeframe]
                            
                            returns = ((end_prices - start_prices) / start_prices * 100).dropna()
                            cumulative_returns[timeframe] = returns.sort_values(ascending=False)
                    
                    except (IndexError, KeyError):
                        logger.warning(f"Could not calculate forward returns for timeframe {timeframe}")
                        continue
        
        except Exception as e:
            logger.error(f"Error calculating cumulative returns: {e}")
        
        return cumulative_returns
    
    def _analyze_timeframe(self, returns_series: pd.Series, sma_data: Dict[str, pd.DataFrame], 
                          timeframe: int, analysis_date: date, direction: str) -> List[Dict[str, Any]]:
        """Analyze a specific timeframe and calculate scores."""
        
        results = []
        
        # Convert series to dataframe for easier manipulation
        returns_df = returns_series.to_frame('cumulative_return')
        returns_df['rank_position'] = range(1, len(returns_df) + 1)
        
        for coin_id, row in returns_df.iterrows():
            cumulative_return = row['cumulative_return']
            rank_position = row['rank_position']
            
            # Calculate day rank score based on position
            day_rank_score = self._calculate_day_rank_score(rank_position)
            
            # Get SMA scores for this coin
            sma_scores = self._calculate_sma_scores(coin_id, sma_data, analysis_date)
            
            # Calculate total score
            total_score = (
                day_rank_score + 
                sma_scores['fast'] + 
                sma_scores['medium'] + 
                sma_scores['slow']
            )
            
            result = {
                'coin_id': coin_id,
                'timeframe': timeframe,
                'cumulative_return': float(cumulative_return),
                'rank_position': rank_position,
                'day_rank_score': day_rank_score,
                'sma_fast_score': sma_scores['fast'],
                'sma_medium_score': sma_scores['medium'],
                'sma_slow_score': sma_scores['slow'],
                'total_score': total_score
            }
            
            results.append(result)
        
        return results
    
    def _calculate_day_rank_score(self, rank_position: int) -> int:
        """Calculate score based on ranking position."""
        if rank_position <= 10:
            return self.config.rank_scores['top_10']
        elif rank_position <= 15:
            return self.config.rank_scores['top_15']
        elif rank_position <= 20:
            return self.config.rank_scores['top_20']
        else:
            return self.config.rank_scores['other']
    
    def _calculate_sma_scores(self, coin_id: str, sma_data: Dict[str, pd.DataFrame], 
                            analysis_date: date) -> Dict[str, int]:
        """Calculate SMA scores for a specific coin."""
        scores = {'fast': 0, 'medium': 0, 'slow': 0}
        
        try:
            # Get the closest date to analysis_date
            for sma_type, df in sma_data.items():
                if coin_id in df.columns and not df.empty:
                    # Find closest date
                    closest_date_idx = df.index.get_indexer([analysis_date], method='nearest')[0]
                    if closest_date_idx >= 0:
                        signal_value = df.iloc[closest_date_idx][coin_id]
                        
                        if pd.notna(signal_value):
                            if sma_type == 'above_sma_6':
                                scores['fast'] = int(signal_value) if signal_value > 0 else int(signal_value)
                            elif sma_type == 'above_sma_11':
                                scores['medium'] = int(signal_value) if signal_value > 0 else int(signal_value)
                            elif sma_type == 'above_sma_21':
                                scores['slow'] = int(signal_value) if signal_value > 0 else int(signal_value)
        
        except Exception as e:
            logger.warning(f"Error calculating SMA scores for {coin_id}: {e}")
        
        return scores
    
    def _create_final_leaderboard(self, screening_results: List[Dict[str, Any]], 
                                timeframes: List[int]) -> List[Dict[str, Any]]:
        """Create final leaderboard aggregating all timeframes."""
        
        # Group by coin_id and aggregate scores
        coin_aggregates = {}
        
        for result in screening_results:
            coin_id = result['coin_id']
            
            if coin_id not in coin_aggregates:
                coin_aggregates[coin_id] = {
                    'coin_id': coin_id,
                    'total_score': 0,
                    'avg_return': 0,
                    'best_rank': float('inf'),
                    'timeframe_scores': {},
                    'timeframe_returns': {}
                }
            
            # Aggregate data
            coin_aggregates[coin_id]['total_score'] += result['total_score']
            coin_aggregates[coin_id]['avg_return'] += result['cumulative_return']
            coin_aggregates[coin_id]['best_rank'] = min(coin_aggregates[coin_id]['best_rank'], 
                                                       result['rank_position'])
            coin_aggregates[coin_id]['timeframe_scores'][str(result['timeframe'])] = result['total_score']
            coin_aggregates[coin_id]['timeframe_returns'][str(result['timeframe'])] = result['cumulative_return']
        
        # Calculate averages and sort
        leaderboard = []
        for coin_id, data in coin_aggregates.items():
            data['avg_return'] = data['avg_return'] / len(timeframes)
            data['avg_score'] = data['total_score'] / len(timeframes)
            
            leaderboard.append(data)
        
        # Sort by total score (descending)
        leaderboard.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Add final ranking
        for i, coin_data in enumerate(leaderboard):
            coin_data['final_rank'] = i + 1
        
        return leaderboard
    
    def _calculate_statistics(self, screening_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate screening statistics."""
        
        if not screening_results:
            return {}
        
        scores = [result['total_score'] for result in screening_results]
        returns = [result['cumulative_return'] for result in screening_results]
        
        return {
            'total_analyses': len(screening_results),
            'unique_coins': len(set(result['coin_id'] for result in screening_results)),
            'score_stats': {
                'mean': float(np.mean(scores)),
                'std': float(np.std(scores)),
                'min': float(np.min(scores)),
                'max': float(np.max(scores)),
                'median': float(np.median(scores))
            },
            'return_stats': {
                'mean': float(np.mean(returns)),
                'std': float(np.std(returns)),
                'min': float(np.min(returns)),
                'max': float(np.max(returns)),
                'median': float(np.median(returns))
            }
        }
    
    def export_results_to_excel(self, analysis_results: Dict[str, Any], 
                               output_path: str = 'data/outputs/screening_results.xlsx') -> bool:
        """Export screening results to Excel format."""
        
        try:
            logger.info(f"Exporting screening results to {output_path}")
            
            leaderboard = analysis_results.get('leaderboard', [])
            if not leaderboard:
                logger.warning("No leaderboard data to export")
                return False
            
            # Create main leaderboard DataFrame
            leaderboard_df = pd.DataFrame(leaderboard)
            
            # Create timeframe breakdown
            timeframe_data = {}
            for coin_data in leaderboard:
                coin_id = coin_data['coin_id']
                for timeframe, score in coin_data.get('timeframe_scores', {}).items():
                    if timeframe not in timeframe_data:
                        timeframe_data[timeframe] = {}
                    timeframe_data[timeframe][coin_id] = {
                        'score': score,
                        'return': coin_data['timeframe_returns'].get(timeframe, 0)
                    }
            
            # Export to Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Main leaderboard
                leaderboard_df.to_excel(writer, sheet_name='Leaderboard', index=False)
                
                # Timeframe breakdown
                for timeframe, data in timeframe_data.items():
                    timeframe_df = pd.DataFrame.from_dict(data, orient='index')
                    timeframe_df.to_excel(writer, sheet_name=f'{timeframe}d')
                
                # Statistics
                if 'statistics' in analysis_results:
                    stats_df = pd.DataFrame([analysis_results['statistics']])
                    stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
            logger.info(f"Successfully exported screening results to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting results to Excel: {e}")
            return False