import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/config.dart';
import '../models/game_state.dart';

class GameService {
  final String token;

  GameService(this.token);

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      };

  Future<Map<String, dynamic>> createGame({int maxRounds = 5}) async {
    final res = await http.post(
      Uri.parse('$kBaseUrl/api/v1/games/create'),
      headers: _headers,
      body: jsonEncode({'max_rounds': maxRounds}),
    );
    _assertOk(res);
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> createVsBotGame({int maxRounds = 5}) async {
    final res = await http.post(
      Uri.parse('$kBaseUrl/api/v1/games/vs-bot'),
      headers: _headers,
      body: jsonEncode({'max_rounds': maxRounds}),
    );
    _assertOk(res);
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> joinGame(String roomCode) async {
    final res = await http.post(
      Uri.parse('$kBaseUrl/api/v1/games/join/$roomCode'),
      headers: _headers,
    );
    _assertOk(res);
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  Future<void> startGame(int gameId) async {
    final res = await http.post(
      Uri.parse('$kBaseUrl/api/v1/games/$gameId/start'),
      headers: _headers,
    );
    _assertOk(res);
  }

  Future<PlayResult> playCard(int gameId, int cardIndex) async {
    final res = await http.post(
      Uri.parse('$kBaseUrl/api/v1/games/$gameId/play?card_index=$cardIndex'),
      headers: _headers,
    );
    _assertOk(res);
    return PlayResult.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }

  Future<GameState> getState(int gameId) async {
    final res = await http.get(
      Uri.parse('$kBaseUrl/api/v1/games/$gameId/state'),
      headers: _headers,
    );
    _assertOk(res);
    return GameState.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }

  Future<List<Map<String, dynamic>>> getMyGames() async {
    final res = await http.get(
      Uri.parse('$kBaseUrl/api/v1/games/my-games'),
      headers: _headers,
    );
    _assertOk(res);
    return (jsonDecode(res.body) as List).cast<Map<String, dynamic>>();
  }

  void _assertOk(http.Response res) {
    if (res.statusCode < 200 || res.statusCode >= 300) {
      final body = jsonDecode(res.body);
      throw Exception(body['detail'] ?? 'Request failed (${res.statusCode})');
    }
  }
}
