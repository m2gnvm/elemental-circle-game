#!/usr/bin/env python3

import requests
import json
import random
import time
import argparse
from typing import Dict, List, Optional

BASE_URL = "http://localhost:8000"

class AISimulator:
    def __init__(self, num_fights: int = 10):
        self.num_fights = num_fights
        self.results = []
        
    def make_request(self, method: str, url: str, headers: Dict = None, data: Dict = None) -> tuple:
        """Make HTTP request and return (status_code, response)"""
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                if "token" in url:
                    # For login, use form data
                    response = requests.post(url, headers=headers, data=data)
                else:
                    # For other requests, use JSON
                    response = requests.post(url, headers=headers, json=data)
            else:
                return 0, None
                
            if response.status_code == 200:
                return response.status_code, response.json()
            else:
                return response.status_code, response.json()
        except Exception as e:
            print(f"Request failed: {e}")
            return 0, None
    
    def check_backend_health(self) -> bool:
        """Check if backend is running"""
        status, response = self.make_request("GET", f"{BASE_URL}/health")
        if status == 200:
            print(f"✅ Backend running: {response}")
            return True
        else:
            print(f"❌ Backend health failed: {response}")
            return False
    
    def register_ai_player(self, player_name: str) -> Optional[str]:
        """Register an AI player and return token"""
        # Make username unique with timestamp
        import time
        timestamp = int(time.time() * 1000)  # milliseconds
        unique_id = f"{player_name}_{timestamp}"
        
        # Register user
        user_data = {
            "username": f"ai_{unique_id}",
            "email": f"ai_{unique_id}@example.com",
            "password": "ai_password"
        }
        
        status, response = self.make_request("POST", f"{BASE_URL}/api/v1/auth/register", data=user_data)
        if status != 200:
            print(f"❌ AI {player_name} registration failed: {response}")
            return None
        else:
            print(f"✅ AI {player_name} registered successfully")
        
        # Login to get token
        login_data = {
            "username": f"ai_{unique_id}",
            "password": "ai_password"
        }
        
        status, response = self.make_request("POST", f"{BASE_URL}/api/v1/auth/token", data=login_data)
        if status == 200:
            print(f"✅ AI {player_name} logged in successfully")
            return response.get("access_token")
        else:
            print(f"❌ AI {player_name} login failed: {response}")
            return None
    
    def create_game(self, token: str, max_rounds: int = 5) -> Optional[Dict]:
        """Create a game and return game info"""
        headers = {"Authorization": f"Bearer {token}"}
        game_data = {"max_rounds": max_rounds}
        
        status, response = self.make_request("POST", f"{BASE_URL}/api/v1/games/create", headers=headers, data=game_data)
        if status == 200:
            return response
        else:
            print(f"❌ Game creation failed: {response}")
            return None
    
    def join_game(self, token: str, room_code: str) -> Optional[Dict]:
        """Join a game"""
        headers = {"Authorization": f"Bearer {token}"}
        
        status, response = self.make_request("POST", f"{BASE_URL}/api/v1/games/join/{room_code}", headers=headers)
        if status == 200:
            return response
        else:
            print(f"❌ Join game failed: {response}")
            return None
    
    def start_game(self, token: str, game_id: int) -> bool:
        """Start the game"""
        headers = {"Authorization": f"Bearer {token}"}
        
        status, response = self.make_request("POST", f"{BASE_URL}/api/v1/games/{game_id}/start", headers=headers)
        if status == 200:
            return True
        else:
            print(f"❌ Start game failed: {response}")
            return False
    
    def get_game_state(self, token: str, game_id: int) -> Optional[Dict]:
        """Get current game state"""
        headers = {"Authorization": f"Bearer {token}"}
        
        status, response = self.make_request("GET", f"{BASE_URL}/api/v1/games/{game_id}/state", headers=headers)
        if status == 200:
            return response
        else:
            return None
    
    def ai_choose_card(self, hand: List[Dict], strategy: str = "random") -> int:
        """AI chooses a card based on strategy"""
        if strategy == "random":
            return random.randint(0, len(hand) - 1)
        elif strategy == "highest":
            # Choose highest value card
            max_value = max(card["value"] for card in hand)
            for i, card in enumerate(hand):
                if card["value"] == max_value:
                    return i
        elif strategy == "lowest":
            # Choose lowest value card
            min_value = min(card["value"] for card in hand)
            for i, card in enumerate(hand):
                if card["value"] == min_value:
                    return i
        elif strategy == "balanced":
            # Choose middle value card
            values = [card["value"] for card in hand]
            values.sort()
            middle_value = values[len(values) // 2]
            for i, card in enumerate(hand):
                if card["value"] == middle_value:
                    return i
        else:
            return random.randint(0, len(hand) - 1)
    
    def play_card(self, token: str, game_id: int, card_index: int) -> Optional[Dict]:
        """Play a card"""
        headers = {"Authorization": f"Bearer {token}"}
        
        status, response = self.make_request("POST", f"{BASE_URL}/api/v1/games/{game_id}/play?card_index={card_index}", headers=headers)
        if status == 200:
            return response
        else:
            return None
    
    def simulate_single_fight(self, ai1_strategy: str, ai2_strategy: str, max_rounds: int = 5) -> Dict:
        """Simulate a single AI vs AI fight"""
        print(f"\n🤖 AI Fight: {ai1_strategy.upper()} vs {ai2_strategy.upper()}")
        print("="*50)
        
        # Register AI players
        ai1_token = self.register_ai_player("player1")
        ai2_token = self.register_ai_player("player2")
        
        if not ai1_token or not ai2_token:
            return {"error": "Failed to register AI players"}
        
        # Create game
        game_info = self.create_game(ai1_token, max_rounds)
        if not game_info:
            return {"error": "Failed to create game"}
        
        game_id = game_info["game_id"]
        
        # AI2 joins game
        room_code = game_info["room_code"]
        join_result = self.join_game(ai2_token, room_code)
        if not join_result:
            return {"error": "Failed to join game"}
        
        # Start game
        if not self.start_game(ai1_token, game_id):
            return {"error": "Failed to start game"}
        
        print(f"🎮 Game started! {max_rounds} rounds max")
        
        # Simulate the fight
        round_num = 1
        while round_num <= max_rounds:
            print(f"\n🔄 ROUND {round_num}")
            print("-" * 30)
            
            # Get game state
            state = self.get_game_state(ai1_token, game_id)
            if not state:
                print("❌ Failed to get game state")
                break
            
            # Check if game is finished
            if state.get("status") == "finished":
                print("🏁 Game finished!")
                break
            
            # Determine turn order (alternate each round)
            if round_num % 2 == 1:
                # Odd rounds: AI1 goes first
                first_player = "AI1"
                second_player = "AI2"
                first_token = ai1_token
                second_token = ai2_token
                first_strategy = ai1_strategy
                second_strategy = ai2_strategy
            else:
                # Even rounds: AI2 goes first
                first_player = "AI2"
                second_player = "AI1"
                first_token = ai2_token
                second_token = ai1_token
                first_strategy = ai2_strategy
                second_strategy = ai1_strategy
            
            print(f"🎯 {first_player} goes first (onboard card)")
            print(f"🤖 {second_player} will counter-play")
            
            # First player plays onboard card
            first_state = self.get_game_state(first_token, game_id)
            if not first_state or not first_state.get('your_hand'):
                print("❌ First player has no cards")
                break
            
            first_hand = first_state['your_hand']
            first_card_index = self.ai_choose_card(first_hand, first_strategy)
            first_card = first_hand[first_card_index]
            
            print(f"🎴 {first_player} plays: {first_card['value']} {first_card['element'].upper()}")
            
            # Play first card
            first_result = self.play_card(first_token, game_id, first_card_index)
            if not first_result:
                print(f"❌ {first_player} play failed")
                break
            
            # Second player plays counter card
            second_state = self.get_game_state(second_token, game_id)
            if not second_state or not second_state.get('your_hand'):
                print("❌ Second player has no cards")
                break
            
            second_hand = second_state['your_hand']
            second_card_index = self.ai_choose_card(second_hand, second_strategy)
            second_card = second_hand[second_card_index]
            
            print(f"🎴 {second_player} plays: {second_card['value']} {second_card['element'].upper()}")
            
            # Play second card
            second_result = self.play_card(second_token, game_id, second_card_index)
            if not second_result:
                print(f"❌ {second_player} play failed")
                break
            
            # Show battle results
            points = second_result.get('points', 0)
            print(f"⚔️ Battle: {second_player} gets {points} points")
            
            # Check if game finished
            if second_result.get('game_finished'):
                print("🏁 Game finished!")
                break
            
            round_num += 1
        
        # Get final results
        final_state = self.get_game_state(ai1_token, game_id)
        if final_state and final_state.get("players"):
            players = final_state["players"]
            ai1_points = players[0].get('points', 0) if len(players) > 0 else 0
            ai2_points = players[1].get('points', 0) if len(players) > 1 else 0
            
            print(f"\n🏆 FINAL RESULTS")
            print(f"🤖 {ai1_strategy.upper()}: {ai1_points} points")
            print(f"🤖 {ai2_strategy.upper()}: {ai2_points} points")
            
            if ai1_points > ai2_points:
                winner = ai1_strategy
                print(f"🏆 {ai1_strategy.upper()} WINS!")
            elif ai2_points > ai1_points:
                winner = ai2_strategy
                print(f"🏆 {ai2_strategy.upper()} WINS!")
            else:
                winner = "tie"
                print("🤝 IT'S A TIE!")
            
            return {
                "ai1_strategy": ai1_strategy,
                "ai2_strategy": ai2_strategy,
                "ai1_points": ai1_points,
                "ai2_points": ai2_points,
                "winner": winner,
                "rounds_played": round_num - 1
            }
        
        return {"error": "Failed to get final results"}
    
    def run_simulations(self):
        """Run multiple AI vs AI simulations"""
        print("🎮 AI vs AI Fight Simulator")
        print("="*60)
        
        if not self.check_backend_health():
            return
        
        strategies = ["random", "highest", "lowest", "balanced"]
        
        print(f"\n🤖 Running {self.num_fights} AI vs AI fights...")
        print("Strategies: random, highest, lowest, balanced")
        print("="*60)
        
        for i in range(self.num_fights):
            print(f"\n🔥 FIGHT {i+1}/{self.num_fights}")
            
            # Randomly select two different strategies
            ai1_strategy = random.choice(strategies)
            ai2_strategy = random.choice([s for s in strategies if s != ai1_strategy])
            
            result = self.simulate_single_fight(ai1_strategy, ai2_strategy)
            self.results.append(result)
            
            # Small delay between fights
            time.sleep(0.5)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print simulation summary"""
        print("\n" + "="*60)
        print("📊 SIMULATION SUMMARY")
        print("="*60)
        
        # Count wins by strategy
        strategy_wins = {}
        total_fights = len(self.results)
        
        for result in self.results:
            if "error" in result:
                continue
            
            winner = result["winner"]
            if winner != "tie":
                strategy_wins[winner] = strategy_wins.get(winner, 0) + 1
        
        print(f"Total fights: {total_fights}")
        print(f"Successful fights: {len([r for r in self.results if 'error' not in r])}")
        
        print("\n🏆 Strategy Performance:")
        for strategy, wins in sorted(strategy_wins.items(), key=lambda x: x[1], reverse=True):
            win_rate = (wins / total_fights) * 100
            print(f"  {strategy.upper()}: {wins} wins ({win_rate:.1f}%)")
        
        ties = len([r for r in self.results if r.get("winner") == "tie"])
        if ties > 0:
            tie_rate = (ties / total_fights) * 100
            print(f"  TIES: {ties} ({tie_rate:.1f}%)")
        
        print("\n🎯 Recent Fights:")
        for i, result in enumerate(self.results[-5:], 1):
            if "error" in result:
                print(f"  Fight {i}: ERROR - {result['error']}")
            else:
                print(f"  Fight {i}: {result['ai1_strategy'].upper()} ({result['ai1_points']}) vs {result['ai2_strategy'].upper()} ({result['ai2_points']}) → {result['winner'].upper()}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Simulate AI vs AI fights")
    parser.add_argument("--fights", "-f", type=int, default=10, help="Number of fights to simulate (default: 10)")
    parser.add_argument("--rounds", "-r", type=int, default=5, help="Number of rounds per fight (default: 5)")
    
    args = parser.parse_args()
    
    simulator = AISimulator(args.fights)
    simulator.run_simulations()

if __name__ == "__main__":
    main()
