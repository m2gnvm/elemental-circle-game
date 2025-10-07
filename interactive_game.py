#!/usr/bin/env python3
"""
Interactive Elemental Circle Game
You choose cards, AI makes random choices
Real backend integration with interactive gameplay
"""

import urllib.request
import urllib.parse
import json
import time
import random
import sys
import argparse
from typing import Dict, List, Optional

BASE_URL = "http://localhost:8000"

class InteractiveGame:
    def __init__(self, max_rounds: int = 5):
        self.player_token = None
        self.ai_token = None
        self.game_id = None
        self.room_code = None
        self.player_id = None
        self.ai_player_id = None
        self.max_rounds = max_rounds
        self.player_goes_first = None  # Will be determined by coin toss
        
    def make_request(self, method: str, url: str, data: Dict = None, headers: Dict = None) -> tuple:
        """Make HTTP request and return (status_code, response_data)"""
        if headers is None:
            headers = {}
        
        if data:
            if method == "POST" and "token" in url:
                # For login, use form data
                form_data = urllib.parse.urlencode(data).encode('utf-8')
                req = urllib.request.Request(url, data=form_data, method=method)
                req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            else:
                # For other requests, use JSON
                json_data = json.dumps(data).encode('utf-8')
                req = urllib.request.Request(url, data=json_data, method=method)
                req.add_header('Content-Type', 'application/json')
        else:
            req = urllib.request.Request(url, method=method)
        
        # Add headers
        for key, value in headers.items():
            req.add_header(key, value)
        
        try:
            with urllib.request.urlopen(req) as response:
                response_data = response.read().decode('utf-8')
                try:
                    return response.status, json.loads(response_data)
                except json.JSONDecodeError:
                    return response.status, {"detail": response_data}
        except urllib.error.HTTPError as e:
            error_data = e.read().decode('utf-8')
            try:
                return e.code, json.loads(error_data)
            except json.JSONDecodeError:
                return e.code, {"detail": error_data}
        except Exception as e:
            return None, {"detail": str(e)}
    
    def register_user(self, username: str, email: str, password: str) -> bool:
        """Register a new user"""
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        
        status, response = self.make_request("POST", f"{BASE_URL}/api/v1/auth/register", data)
        
        if status == 200:
            return True
        else:
            # User might already exist, continue
            return True
    
    def login_user(self, username: str, password: str) -> Optional[str]:
        """Login user and return token"""
        login_data = {
            "username": username,
            "password": password
        }
        
        status, response = self.make_request("POST", f"{BASE_URL}/api/v1/auth/token", login_data)
        
        if status == 200:
            return response.get("access_token")
        else:
            return None
    
    def create_game(self) -> bool:
        """Create a new game"""
        print("🎮 Creating game room...")
        
        headers = {"Authorization": f"Bearer {self.player_token}"}
        data = {"max_rounds": self.max_rounds}
        status, response = self.make_request("POST", f"{BASE_URL}/api/v1/games/create", data, headers)
        
        if status == 200:
            self.game_id = response.get("game_id")
            self.room_code = response.get("room_code")
            self.player_id = response.get("player_id")
            print(f"✅ Game created - Room Code: {self.room_code}")
            return True
        else:
            print(f"❌ Game creation failed: {response.get('detail', 'Unknown error')}")
            return False
    
    def join_game(self) -> bool:
        """AI player joins the game"""
        print("🤖 AI player joining game...")
        
        headers = {"Authorization": f"Bearer {self.ai_token}"}
        status, response = self.make_request("POST", f"{BASE_URL}/api/v1/games/join/{self.room_code}", headers=headers)
        
        if status == 200:
            self.ai_player_id = response.get("player_id")
            print("✅ AI player joined")
            return True
        else:
            print(f"❌ AI join failed: {response.get('detail', 'Unknown error')}")
            return False
    
    def start_game(self) -> bool:
        """Start the game"""
        print("🚀 Starting the game...")
        
        headers = {"Authorization": f"Bearer {self.player_token}"}
        status, response = self.make_request("POST", f"{BASE_URL}/api/v1/games/{self.game_id}/start", headers=headers)
        
        if status == 200:
            print("✅ Game started! Cards dealt to players.")
            return True
        else:
            print(f"❌ Start game failed: {response.get('detail', 'Unknown error')}")
            return False
    
    def get_game_state(self, token: str) -> Optional[Dict]:
        """Get current game state"""
        headers = {"Authorization": f"Bearer {token}"}
        status, response = self.make_request("GET", f"{BASE_URL}/api/v1/games/{self.game_id}/state", headers=headers)
        
        if status == 200:
            return response
        else:
            return None
    
    def play_card(self, token: str, card_index: int) -> Optional[Dict]:
        """Play a card"""
        headers = {"Authorization": f"Bearer {token}"}
        status, response = self.make_request("POST", f"{BASE_URL}/api/v1/games/{self.game_id}/play?card_index={card_index}", headers=headers)
        
        if status == 200:
            return response
        else:
            return None
    
    def display_game_state(self, state: Dict):
        """Display current game state"""
        print("\n" + "="*60)
        print("🎮 ELEMENTAL CIRCLE GAME")
        print("="*60)
        
        # Game info
        print(f"📊 Game Status: {state.get('status', 'unknown').upper()}")
        print(f"🔄 Round: {state.get('round', 1)}")
        print(f"🎯 Turn: {state.get('turn', 1)}")
        
        # Onboard card
        onboard_card = state.get('onboard_card')
        if onboard_card:
            print(f"🃏 Onboard Card: {onboard_card['value']} {onboard_card['element'].upper()}")
        else:
            print("🃏 Onboard Card: None")
        
        # Players info
        players = state.get('players', [])
        print(f"\n👥 Players:")
        
        # Find your player and AI player
        your_player = next((p for p in players if p['id'] == self.player_id), None)
        ai_player = next((p for p in players if p['id'] == self.ai_player_id), None)
        
        if your_player:
            print(f"   You: {your_player.get('points', 0)} points, {your_player.get('cards_in_hand', 0)} cards")
        if ai_player:
            print(f"   AI: {ai_player.get('points', 0)} points, {ai_player.get('cards_in_hand', 0)} cards")
        
        # Your hand
        hand = state.get('your_hand', [])
        if hand:
            print(f"\n🎴 Your Hand ({len(hand)} cards):")
            for i, card in enumerate(hand):
                print(f"   {i}: {card['value']} {card['element'].upper()}")
        else:
            print("\n🎴 Your Hand: Empty")
        
        print("="*60)
    
    def display_card_battle(self, result: Dict, player_name: str, opponent_card: Dict = None):
        """Display card battle results with opponent's card"""
        print(f"\n⚔️ {player_name} CARD BATTLE:")
        
        # Show what opponent played
        if opponent_card:
            print(f"🤖 AI played: {opponent_card['value']} {opponent_card['element']}")
        
        points = result.get('points', 0)
        total_points = result.get('player_points', 0)
        print(f"📊 Points this turn: {points}")
        print(f"🏆 Total points: {total_points}")
        
        if result.get('game_finished'):
            print("🏁 GAME FINISHED!")
    
    def get_user_card_choice(self, hand: List[Dict]) -> int:
        """Get user's card choice"""
        while True:
            try:
                print(f"\n🎯 Choose a card to play (0-{len(hand)-1}):")
                choice = int(input("Your choice: "))
                if 0 <= choice < len(hand):
                    return choice
                else:
                    print(f"❌ Please enter a number between 0 and {len(hand)-1}")
            except ValueError:
                print("❌ Please enter a valid number")
    
    def ai_choose_card(self, hand: List[Dict]) -> int:
        """AI chooses a card randomly"""
        return random.randint(0, len(hand) - 1)
    
    def get_ai_hand(self) -> List[Dict]:
        """Get AI's current hand"""
        ai_state = self.get_game_state(self.ai_token)
        if ai_state:
            return ai_state.get('your_hand', [])
        return []
    
    def coin_toss(self) -> bool:
        """Coin toss to determine who goes first"""
        print("\n🪙 COIN TOSS TO DETERMINE WHO GOES FIRST")
        print("="*50)
        print("🪙 Flipping coin...")
        time.sleep(1)
        
        self.player_goes_first = random.choice([True, False])
        
        if self.player_goes_first:
            print("🎯 HEADS! You go first (you play the onboard card)")
            print("🤖 AI will counter-play")
        else:
            print("🎯 TAILS! AI goes first (AI plays the onboard card)")
            print("🎯 You will counter-play")
        
        print("="*50)
        return self.player_goes_first
    
    def setup_players(self):
        """Setup player and AI"""
        print("🔧 Setting up players...")
        
        # Player (You)
        username = "player"
        email = "player@game.com"
        password = "gamepass123"
        
        # AI Player
        ai_username = f"ai_{random.randint(1000, 9999)}"
        ai_email = f"{ai_username}@ai.com"
        ai_password = "aipass123"
        
        # Register players
        self.register_user(username, email, password)
        self.register_user(ai_username, ai_email, ai_password)
        
        # Login players
        self.player_token = self.login_user(username, password)
        self.ai_token = self.login_user(ai_username, ai_password)
        
        if not self.player_token or not self.ai_token:
            print("❌ Failed to setup players")
            return False
        
        print("✅ Players setup complete")
        return True
    
    def play_interactive_game(self):
        """Play the interactive game"""
        print("🎮 Elemental Circle Interactive Game")
        print("🌱 Grass > Water > Fire > Grass")
        print("="*60)
        print("🎯 You vs AI - Choose your cards!")
        print("="*60)
        
        # Setup
        if not self.setup_players():
            return
        
        # Create and join game
        if not self.create_game():
            return
        
        if not self.join_game():
            return
        
        # Coin toss to determine who goes first
        self.coin_toss()
        
        # Start game
        if not self.start_game():
            return
        
        print(f"\n🎯 Game started! You vs AI ({self.max_rounds} rounds max)")
        print("="*60)
        
        # Game loop
        round_num = 1
        while round_num <= self.max_rounds:
            print(f"\n🔄 ROUND {round_num}")
            print("="*40)
            
            # Get game state
            state = self.get_game_state(self.player_token)
            if not state:
                print("❌ Failed to get game state")
                break
            
            # Display current state
            self.display_game_state(state)
            
            # Check if game is finished
            if state.get("status") == "finished":
                print("🏁 Game finished!")
                break
            
            # Determine turn order for this round (alternate each round)
            if round_num % 2 == 1:
                # Odd rounds: use original coin toss result
                if self.player_goes_first:
                    print("🎯 You go first (onboard card) - AI will counter-play")
                    player_first = True
                else:
                    print("🤖 AI goes first (onboard card) - You will counter-play")
                    player_first = False
            else:
                # Even rounds: reverse the order
                if self.player_goes_first:
                    print("🤖 AI goes first (onboard card) - You will counter-play")
                    player_first = False
                else:
                    print("🎯 You go first (onboard card) - AI will counter-play")
                    player_first = True
            
            hand = state.get('your_hand', [])
            if not hand:
                print("❌ No cards in hand")
                break
            
            ai_hand = self.get_ai_hand()
            if not ai_hand:
                print("❌ AI has no cards")
                break
            
            # Play cards based on turn order
            if player_first:
                # You play first (onboard), AI counters
                print(f"\n🎯 Your turn to play the onboard card:")
                card_index = self.get_user_card_choice(hand)
                played_card = hand[card_index]
                print(f"🎴 You play: {played_card['value']} {played_card['element'].upper()}")
                
                # Play your card
                result = self.play_card(self.player_token, card_index)
                if not result:
                    break
                
                # Get fresh AI hand after your play
                ai_hand = self.get_ai_hand()
                if not ai_hand:
                    print("❌ AI has no cards")
                    break
                
                # AI chooses counter card and plays it
                ai_card_index = self.ai_choose_card(ai_hand)
                ai_card = ai_hand[ai_card_index]
                print(f"🤖 AI plays: {ai_card['value']} {ai_card['element'].upper()}")
                
                # AI plays their card
                ai_result = self.play_card(self.ai_token, ai_card_index)
                if not ai_result:
                    break
                
                # Display battle results with AI's card
                self.display_card_battle(result, "You", ai_card)
                
                # Check if game finished after both players played
                if ai_result.get('game_finished'):
                    print("🏁 Game finished!")
                    break
            else:
                # AI plays first (onboard), you counter
                ai_card_index = self.ai_choose_card(ai_hand)
                ai_card = ai_hand[ai_card_index]
                print(f"🤖 AI plays: {ai_card['value']} {ai_card['element'].upper()}")
                
                # AI plays their card first
                ai_result = self.play_card(self.ai_token, ai_card_index)
                if not ai_result:
                    break
                
                # Get fresh hand after AI play
                fresh_state = self.get_game_state(self.player_token)
                if not fresh_state:
                    print("❌ Failed to get fresh game state")
                    break
                
                fresh_hand = fresh_state.get('your_hand', [])
                if not fresh_hand:
                    print("❌ No cards in hand")
                    break
                
                print(f"\n🎯 Your turn to counter-play:")
                card_index = self.get_user_card_choice(fresh_hand)
                played_card = fresh_hand[card_index]
                print(f"🎴 You play: {played_card['value']} {played_card['element'].upper()}")
                
                # Play your card
                result = self.play_card(self.player_token, card_index)
                if not result:
                    break
                
                # Display battle results with AI's card
                self.display_card_battle(result, "You", ai_card)
                
                # Check if game finished after both players played
                if result.get('game_finished'):
                    print("🏁 Game finished!")
                    break
            
            round_num += 1
            
            # Safety check
            if round_num > self.max_rounds + 5:
                print("⚠️ Game taking too long, stopping simulation")
                break
        
        # Final results
        print("\n🏆 FINAL RESULTS")
        print("="*50)
        final_state = self.get_game_state(self.player_token)
        if final_state and final_state.get("players"):
            players = final_state["players"]
            
            # Find your player and AI player
            your_player = next((p for p in players if p['id'] == self.player_id), None)
            ai_player = next((p for p in players if p['id'] == self.ai_player_id), None)
            
            your_points = your_player.get('points', 0) if your_player else 0
            ai_points = ai_player.get('points', 0) if ai_player else 0
            
            print(f"👤 Your Points: {your_points}")
            print(f"🤖 AI Points: {ai_points}")
            
            if your_points > ai_points:
                print("🏆 YOU WIN!")
            elif ai_points > your_points:
                print("🤖 AI WINS!")
            else:
                print("🤝 IT'S A TIE!")
        
        print("\n✅ Game completed!")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Elemental Circle Interactive Game')
    parser.add_argument('--rounds', '-r', type=int, default=5, 
                       help='Number of rounds to play (default: 5)')
    args = parser.parse_args()
    
    print("🎮 Elemental Circle Interactive Game")
    print("You choose cards, AI makes random choices")
    print("="*70)
    
    # Check if backend is running
    try:
        with urllib.request.urlopen(f"{BASE_URL}/health") as response:
            health_data = json.loads(response.read().decode('utf-8'))
            print(f"✅ Backend running: {health_data}")
    except:
        print("❌ Backend not running. Start it with: python -m app.main")
        return
    
    # Start the interactive game
    game = InteractiveGame(max_rounds=args.rounds)
    game.play_interactive_game()

if __name__ == "__main__":
    main()
