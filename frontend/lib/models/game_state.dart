import 'card_model.dart';

class PlayerInfo {
  final int id;
  final String username;
  final double points;
  final int cardsInHand;

  const PlayerInfo({
    required this.id,
    required this.username,
    required this.points,
    required this.cardsInHand,
  });

  factory PlayerInfo.fromJson(Map<String, dynamic> json) => PlayerInfo(
        id: json['id'] as int,
        username: json['username'] as String,
        points: (json['points'] as num).toDouble(),
        cardsInHand: json['cards_in_hand'] as int,
      );
}

class GameState {
  final int gameId;
  final String status;
  final int round;
  final int turn;
  final CardModel? onboardCard;
  final List<PlayerInfo> players;
  final List<CardModel> yourHand;

  const GameState({
    required this.gameId,
    required this.status,
    required this.round,
    required this.turn,
    this.onboardCard,
    required this.players,
    required this.yourHand,
  });

  factory GameState.fromJson(Map<String, dynamic> json) => GameState(
        gameId: json['game_id'] as int,
        status: json['status'] as String,
        round: json['round'] as int,
        turn: json['turn'] as int,
        onboardCard: json['onboard_card'] != null
            ? CardModel.fromJson(json['onboard_card'] as Map<String, dynamic>)
            : null,
        players: (json['players'] as List)
            .map((p) => PlayerInfo.fromJson(p as Map<String, dynamic>))
            .toList(),
        yourHand: json['your_hand'] != null
            ? (json['your_hand'] as List)
                .map((c) => CardModel.fromJson(c as Map<String, dynamic>))
                .toList()
            : [],
      );

  bool get isFinished => status == 'finished';
  bool get isInProgress => status == 'in_progress';
  bool get isWaiting => status == 'waiting';
}

class PlayResult {
  final double points;
  final double playerPoints;
  final CardModel onboardCard;
  final bool gameFinished;
  final int round;
  final int turn;

  const PlayResult({
    required this.points,
    required this.playerPoints,
    required this.onboardCard,
    required this.gameFinished,
    required this.round,
    required this.turn,
  });

  factory PlayResult.fromJson(Map<String, dynamic> json) => PlayResult(
        points: (json['points'] as num).toDouble(),
        playerPoints: (json['player_points'] as num).toDouble(),
        onboardCard:
            CardModel.fromJson(json['onboard_card'] as Map<String, dynamic>),
        gameFinished: json['game_finished'] as bool,
        round: json['round'] as int,
        turn: json['turn'] as int,
      );
}
