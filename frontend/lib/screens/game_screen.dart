import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../core/config.dart';
import '../models/game_state.dart';
import '../services/auth_service.dart';
import '../services/game_service.dart';
import '../widgets/card_widget.dart';
import 'lobby_screen.dart';

class GameScreen extends StatefulWidget {
  final int gameId;
  final bool? youGoFirst;

  const GameScreen({super.key, required this.gameId, this.youGoFirst});

  @override
  State<GameScreen> createState() => _GameScreenState();
}

class _GameScreenState extends State<GameScreen> {
  GameState? _state;
  bool _loading = true;
  bool _playingCard = false;
  int? _selectedCardIndex;
  String? _lastResult;
  WebSocketChannel? _ws;
  Timer? _pollTimer;

  late GameService _gameService;

  @override
  void initState() {
    super.initState();
    _gameService = GameService(context.read<AuthService>().token!);
    _loadState();
    _connectWebSocket();
    // Show coin-flip result briefly
    if (widget.youGoFirst != null) {
      Future.delayed(const Duration(milliseconds: 600), () {
        if (mounted) {
          setState(() {
            _lastResult = widget.youGoFirst!
                ? '🪙 You go first — set the board card!'
                : '🪙 Bot goes first — get ready to counter!';
          });
          Future.delayed(const Duration(seconds: 3), () {
            if (mounted) setState(() => _lastResult = null);
          });
        }
      });
    }
  }

  @override
  void dispose() {
    _ws?.sink.close();
    _pollTimer?.cancel();
    super.dispose();
  }

  void _connectWebSocket() {
    try {
      _ws = WebSocketChannel.connect(
        Uri.parse('$kWsBaseUrl/ws/${widget.gameId}'),
      );
      _ws!.stream.listen(
        (message) {
          // Any incoming message → refresh state
          _loadState();
        },
        onError: (_) => _startPolling(),
        onDone: _startPolling,
      );
    } catch (_) {
      _startPolling();
    }
  }

  void _startPolling() {
    _pollTimer ??= Timer.periodic(
      const Duration(seconds: 3),
      (_) => _loadState(),
    );
  }

  Future<void> _loadState() async {
    try {
      final state = await _gameService.getState(widget.gameId);
      if (mounted) {
        setState(() {
          _state = state;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _startGame() async {
    setState(() => _loading = true);
    try {
      await _gameService.startGame(widget.gameId);
      await _loadState();
    } catch (e) {
      _showError(e);
      setState(() => _loading = false);
    }
  }

  Future<void> _playCard(int index) async {
    if (_playingCard) return;
    setState(() {
      _playingCard = true;
      _selectedCardIndex = index;
      _lastResult = null;
    });
    try {
      final result = await _gameService.playCard(widget.gameId, index);
      final pointsStr = result.points > 0
          ? '+${result.points.toStringAsFixed(1)}'
          : result.points.toStringAsFixed(1);
      setState(() {
        _lastResult = result.points != 0
            ? '$pointsStr pts  •  Total: ${result.playerPoints.toStringAsFixed(0)}'
            : 'Card placed on board';
      });

      // Notify other players via WebSocket
      _ws?.sink.add(jsonEncode({'type': 'state_refresh'}));

      await _loadState();
    } catch (e) {
      _showError(e);
    } finally {
      if (mounted) {
        setState(() {
          _playingCard = false;
          _selectedCardIndex = null;
        });
      }
    }
  }

  void _showError(Object e) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(e.toString().replaceFirst('Exception: ', '')),
        backgroundColor: Colors.redAccent,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: kBgDark,
      body: _loading && _state == null
          ? const Center(
              child: CircularProgressIndicator(color: kAccent),
            )
          : _state == null
              ? _buildErrorState()
              : _buildGameContent(),
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, color: Colors.redAccent, size: 48),
          const SizedBox(height: 16),
          const Text('Failed to load game', style: TextStyle(color: kTextPrimary)),
          const SizedBox(height: 16),
          ElevatedButton(onPressed: _loadState, child: const Text('Retry')),
        ],
      ),
    );
  }

  Widget _buildGameContent() {
    final state = _state!;
    if (state.isWaiting) return _buildWaitingState(state);
    if (state.isFinished) return _buildFinishedState(state);
    return _buildPlayingState(state);
  }

  // ── Waiting state ──────────────────────────────────────────────────────────

  Widget _buildWaitingState(GameState state) {
    final isHost = state.players.isNotEmpty &&
        state.players.first.id ==
            (context.read<AuthService>().username != null
                ? state.players
                    .firstWhere(
                      (p) =>
                          p.username ==
                          context.read<AuthService>().username,
                      orElse: () => state.players.first,
                    )
                    .id
                : state.players.first.id);

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('⚔️', style: TextStyle(fontSize: 56)),
            const SizedBox(height: 20),
            Text(
              'Game Lobby',
              style: const TextStyle(
                color: kTextPrimary,
                fontSize: 26,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Game #${state.gameId}',
              style: TextStyle(color: kTextSecondary, fontSize: 14),
            ),
            const SizedBox(height: 32),
            _buildPlayersList(state),
            const SizedBox(height: 32),
            if (state.players.length < 2) ...[
              _buildWaitingIndicator(),
            ] else ...[
              ElevatedButton.icon(
                onPressed: _loading ? null : _startGame,
                icon: const Icon(Icons.play_arrow),
                label: const Text('Start Game'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: kGrassColor,
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 52),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14)),
                ),
              ),
            ],
            const SizedBox(height: 16),
            TextButton(
              onPressed: () => Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (_) => const LobbyScreen()),
              ),
              child:
                  const Text('Back to Lobby', style: TextStyle(color: kTextSecondary)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPlayersList(GameState state) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: kSurface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        children: [
          for (int i = 0; i < 2; i++)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 6),
              child: Row(
                children: [
                  Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: i < state.players.length
                          ? kAccent.withAlpha(60)
                          : Colors.white10,
                    ),
                    child: Center(
                      child: Text(
                        i < state.players.length
                            ? state.players[i].username[0].toUpperCase()
                            : '?',
                        style: TextStyle(
                          color: i < state.players.length
                              ? kAccent
                              : kTextSecondary,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    i < state.players.length
                        ? state.players[i].username
                        : 'Waiting for player...',
                    style: TextStyle(
                      color: i < state.players.length
                          ? kTextPrimary
                          : kTextSecondary,
                      fontSize: 15,
                      fontStyle: i < state.players.length
                          ? FontStyle.normal
                          : FontStyle.italic,
                    ),
                  ),
                  const Spacer(),
                  if (i < state.players.length)
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: kGrassColor.withAlpha(40),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        'Ready',
                        style: TextStyle(
                            color: kGrassColor,
                            fontSize: 11,
                            fontWeight: FontWeight.bold),
                      ),
                    ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildWaitingIndicator() {
    return Column(
      children: [
        const CircularProgressIndicator(color: kAccent, strokeWidth: 2),
        const SizedBox(height: 12),
        Text(
          'Waiting for opponent to join...',
          style: TextStyle(color: kTextSecondary, fontSize: 13),
        ),
        const SizedBox(height: 6),
        Text(
          'Share the room code from the lobby',
          style: TextStyle(color: kTextSecondary, fontSize: 11),
        ),
      ],
    );
  }

  // ── In-progress state ──────────────────────────────────────────────────────

  Widget _buildPlayingState(GameState state) {
    final myUsername = context.read<AuthService>().username;
    final me = state.players.firstWhere(
      (p) => p.username == myUsername,
      orElse: () => state.players.first,
    );
    final opponent = state.players.firstWhere(
      (p) => p.username != myUsername,
      orElse: () => state.players.last,
    );

    return SafeArea(
      child: Column(
        children: [
          _buildTopBar(state),
          _buildOpponentPanel(opponent),
          Expanded(child: _buildBoardArea(state)),
          if (_lastResult != null) _buildResultBanner(),
          _buildYourPanel(me),
          _buildHand(state),
          const SizedBox(height: 12),
        ],
      ),
    );
  }

  Widget _buildTopBar(GameState state) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      color: kSurface,
      child: Row(
        children: [
          IconButton(
            icon: const Icon(Icons.arrow_back, color: kTextSecondary, size: 20),
            onPressed: () => Navigator.of(context).pushReplacement(
              MaterialPageRoute(builder: (_) => const LobbyScreen()),
            ),
          ),
          const Spacer(),
          _Chip(label: 'Round ${state.round}', color: kAccent),
          const SizedBox(width: 8),
          _Chip(
            label: 'Turn ${state.turn}',
            color: state.turn == 1 ? kFireColor : kWaterColor,
          ),
          const Spacer(),
          IconButton(
            icon: _loading
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child:
                        CircularProgressIndicator(strokeWidth: 2, color: kAccent),
                  )
                : const Icon(Icons.refresh, color: kTextSecondary, size: 20),
            onPressed: _loading ? null : _loadState,
          ),
        ],
      ),
    );
  }

  Widget _buildOpponentPanel(PlayerInfo opponent) {
    final isBot = opponent.username == 'ElementalBot';
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      child: Row(
        children: [
          isBot
              ? Container(
                  width: 38,
                  height: 38,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: kFireColor.withAlpha(40),
                    border: Border.all(color: kFireColor.withAlpha(120)),
                  ),
                  child: const Center(
                    child: Text('🤖', style: TextStyle(fontSize: 18)),
                  ),
                )
              : _Avatar(name: opponent.username, color: kFireColor),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    isBot ? 'ElementalBot' : opponent.username,
                    style: const TextStyle(
                        color: kTextPrimary,
                        fontWeight: FontWeight.bold,
                        fontSize: 15),
                  ),
                  if (isBot) ...[
                    const SizedBox(width: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 6, vertical: 1),
                      decoration: BoxDecoration(
                        color: kFireColor.withAlpha(40),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: const Text(
                        'AI',
                        style: TextStyle(
                            color: kFireColor,
                            fontSize: 10,
                            fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ],
              ),
              Text(
                isBot
                    ? 'Sets the board each round'
                    : '${opponent.cardsInHand} cards in hand',
                style: TextStyle(color: kTextSecondary, fontSize: 12),
              ),
            ],
          ),
          const Spacer(),
          _ScoreBadge(points: opponent.points, color: kFireColor),
        ],
      ),
    );
  }

  Widget _buildBoardArea(GameState state) {
    final myUsername = context.read<AuthService>().username;
    final me = state.players.firstWhere(
      (p) => p.username == myUsername,
      orElse: () => state.players.first,
    );
    final isMyTurn = state.yourHand.isNotEmpty;
    // turn 1 = set board (no score), turn 2 = counter (score)
    final turnLabel = state.turn == 1
        ? (isMyTurn ? '⚔️ Your turn — set the board' : '⏳ Bot is setting the board...')
        : (isMyTurn ? '✨ Your turn — counter & score!' : '⏳ Bot is countering...');

    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            turnLabel,
            style: TextStyle(
              color: state.turn == 2 && isMyTurn ? kGrassColor : kTextSecondary,
              fontSize: 12,
              letterSpacing: 1,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          BoardCard(card: state.onboardCard),
        ],
      ),
    );
  }

  Widget _buildResultBanner() {
    return AnimatedOpacity(
      opacity: _lastResult != null ? 1.0 : 0.0,
      duration: const Duration(milliseconds: 300),
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: kAccent.withAlpha(30),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: kAccent.withAlpha(80)),
        ),
        child: Text(
          _lastResult ?? '',
          textAlign: TextAlign.center,
          style: const TextStyle(
              color: kAccent, fontSize: 13, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }

  Widget _buildYourPanel(PlayerInfo me) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      child: Row(
        children: [
          _Avatar(name: me.username, color: kWaterColor),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(me.username,
                  style: const TextStyle(
                      color: kTextPrimary,
                      fontWeight: FontWeight.bold,
                      fontSize: 15)),
              Text(
                'Your hand',
                style: TextStyle(color: kTextSecondary, fontSize: 12),
              ),
            ],
          ),
          const Spacer(),
          _ScoreBadge(points: me.points, color: kWaterColor),
        ],
      ),
    );
  }

  Widget _buildHand(GameState state) {
    if (state.yourHand.isEmpty) {
      return Padding(
        padding: const EdgeInsets.all(16),
        child: Text(
          'No cards left',
          style: TextStyle(color: kTextSecondary, fontSize: 13),
        ),
      );
    }

    return SizedBox(
      height: 116,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: state.yourHand.length,
        itemBuilder: (_, i) {
          final isSelected = _selectedCardIndex == i;
          return Padding(
            padding: const EdgeInsets.only(right: 10),
            child: CardWidget(
              card: state.yourHand[i],
              isPlayable: !_playingCard,
              isSelected: isSelected,
              onTap: () => _playCard(i),
            ),
          );
        },
      ),
    );
  }

  // ── Finished state ─────────────────────────────────────────────────────────

  Widget _buildFinishedState(GameState state) {
    final myUsername = context.read<AuthService>().username;
    final sorted = [...state.players]
      ..sort((a, b) => b.points.compareTo(a.points));
    final winner = sorted.first;
    final isWinner = winner.username == myUsername;

    return SafeArea(
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                isWinner ? '🏆' : '💀',
                style: const TextStyle(fontSize: 64),
              ),
              const SizedBox(height: 16),
              Text(
                isWinner ? 'Victory!' : 'Defeat',
                style: TextStyle(
                  color: isWinner ? kGrassColor : kFireColor,
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '${winner.username} wins with ${winner.points.toStringAsFixed(0)} pts',
                style: TextStyle(color: kTextSecondary, fontSize: 14),
              ),
              const SizedBox(height: 32),
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: kSurface,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.white10),
                ),
                child: Column(
                  children: [
                    const Text(
                      'Final Scores',
                      style: TextStyle(
                          color: kTextPrimary,
                          fontWeight: FontWeight.bold,
                          fontSize: 15),
                    ),
                    const SizedBox(height: 14),
                    for (int i = 0; i < sorted.length; i++)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 6),
                        child: Row(
                          children: [
                            Text(
                              i == 0 ? '🥇' : '🥈',
                              style: const TextStyle(fontSize: 20),
                            ),
                            const SizedBox(width: 10),
                            Text(
                              sorted[i].username,
                              style: const TextStyle(
                                  color: kTextPrimary, fontSize: 15),
                            ),
                            const Spacer(),
                            Text(
                              '${sorted[i].points.toStringAsFixed(0)} pts',
                              style: TextStyle(
                                color: i == 0 ? kGrassColor : kTextSecondary,
                                fontWeight: FontWeight.bold,
                                fontSize: 15,
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
              const SizedBox(height: 32),
              ElevatedButton.icon(
                onPressed: () => Navigator.of(context).pushReplacement(
                  MaterialPageRoute(builder: (_) => const LobbyScreen()),
                ),
                icon: const Icon(Icons.home),
                label: const Text('Back to Lobby'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: kAccent,
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 52),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Small reusable widgets ────────────────────────────────────────────────────

class _Chip extends StatelessWidget {
  final String label;
  final Color color;

  const _Chip({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withAlpha(30),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withAlpha(80)),
      ),
      child: Text(
        label,
        style: TextStyle(
            color: color, fontSize: 12, fontWeight: FontWeight.bold),
      ),
    );
  }
}

class _Avatar extends StatelessWidget {
  final String name;
  final Color color;

  const _Avatar({required this.name, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 38,
      height: 38,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: color.withAlpha(40),
        border: Border.all(color: color.withAlpha(120)),
      ),
      child: Center(
        child: Text(
          name[0].toUpperCase(),
          style: TextStyle(
              color: color, fontWeight: FontWeight.bold, fontSize: 16),
        ),
      ),
    );
  }
}

class _ScoreBadge extends StatelessWidget {
  final double points;
  final Color color;

  const _ScoreBadge({required this.points, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withAlpha(30),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withAlpha(80)),
      ),
      child: Text(
        '${points.toStringAsFixed(0)} pts',
        style: TextStyle(
            color: color, fontWeight: FontWeight.bold, fontSize: 14),
      ),
    );
  }
}
