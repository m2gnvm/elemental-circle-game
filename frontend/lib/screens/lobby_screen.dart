import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../core/config.dart';
import '../services/auth_service.dart';
import '../services/game_service.dart';
import 'game_screen.dart';
import 'login_screen.dart';

class LobbyScreen extends StatefulWidget {
  const LobbyScreen({super.key});

  @override
  State<LobbyScreen> createState() => _LobbyScreenState();
}

class _LobbyScreenState extends State<LobbyScreen> {
  final _joinCodeCtrl = TextEditingController();
  bool _loading = false;
  String? _createdRoomCode;
  int? _currentGameId;

  @override
  void dispose() {
    _joinCodeCtrl.dispose();
    super.dispose();
  }

  GameService get _gameService =>
      GameService(context.read<AuthService>().token!);

  Future<void> _playVsBot() async {
    setState(() => _loading = true);
    try {
      final result = await _gameService.createVsBotGame();
      final gameId = result['game_id'] as int;
      final youGoFirst = result['you_go_first'] as bool? ?? false;
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (_) => GameScreen(gameId: gameId, youGoFirst: youGoFirst),
          ),
        );
      }
    } catch (e) {
      _showError(e);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _createGame() async {
    setState(() => _loading = true);
    try {
      final result = await _gameService.createGame();
      setState(() {
        _createdRoomCode = result['room_code'] as String;
        _currentGameId = result['game_id'] as int;
      });
    } catch (e) {
      _showError(e);
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _joinGame() async {
    final code = _joinCodeCtrl.text.trim();
    if (code.isEmpty) return;
    setState(() => _loading = true);
    try {
      final result = await _gameService.joinGame(code);
      final gameId = result['game_id'] as int;
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => GameScreen(gameId: gameId)),
        );
      }
    } catch (e) {
      _showError(e);
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _goToCreatedGame() async {
    if (_currentGameId == null) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => GameScreen(gameId: _currentGameId!)),
    );
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
    final auth = context.watch<AuthService>();
    return Scaffold(
      backgroundColor: kBgDark,
      appBar: AppBar(
        backgroundColor: kSurface,
        title: const Text('🔥💧🌿  Elemental Circle'),
        titleTextStyle: const TextStyle(
          color: kTextPrimary,
          fontSize: 18,
          fontWeight: FontWeight.bold,
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: Center(
              child: Text(
                auth.username ?? '',
                style: TextStyle(color: kTextSecondary, fontSize: 13),
              ),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.logout, color: kTextSecondary),
            tooltip: 'Logout',
            onPressed: () async {
              await auth.logout();
              if (mounted) {
                Navigator.of(context).pushReplacement(
                  MaterialPageRoute(builder: (_) => const LoginScreen()),
                );
              }
            },
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _buildWelcomeBanner(auth.username ?? ''),
              const SizedBox(height: 24),
              _buildVsBotSection(),
              const SizedBox(height: 24),
              _buildDivider(),
              const SizedBox(height: 24),
              _buildCreateSection(),
              const SizedBox(height: 24),
              _buildDivider(),
              const SizedBox(height: 24),
              _buildJoinSection(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomeBanner(String username) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [kAccent.withAlpha(40), kCardBg],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: kAccent.withAlpha(60)),
      ),
      child: Row(
        children: [
          const Text('👋', style: TextStyle(fontSize: 28)),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Welcome, $username',
                  style: const TextStyle(
                    color: kTextPrimary,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'Create a game or join with a room code',
                  style: TextStyle(color: kTextSecondary, fontSize: 13),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVsBotSection() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [kFireColor.withAlpha(30), kCardBg],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: kFireColor.withAlpha(80)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              const Text('🤖', style: TextStyle(fontSize: 22)),
              const SizedBox(width: 10),
              const Text(
                'Play vs Bot',
                style: TextStyle(
                  color: kTextPrimary,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: kFireColor.withAlpha(40),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: kFireColor.withAlpha(100)),
                ),
                child: const Text(
                  'INSTANT',
                  style: TextStyle(
                    color: kFireColor,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Face ElementalBot — it plays the strongest card every round. You counter and score.',
            style: TextStyle(color: kTextSecondary, fontSize: 13),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: _loading ? null : _playVsBot,
            icon: _loading
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                        strokeWidth: 2, color: Colors.white),
                  )
                : const Text('🤖', style: TextStyle(fontSize: 16)),
            label: const Text(
              'Play vs Bot',
              style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: kFireColor,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCreateSection() {
    return _Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const _SectionTitle(icon: '⚔️', title: 'Create Game'),
          const SizedBox(height: 16),
          if (_createdRoomCode != null) ...[
            _buildRoomCodeDisplay(),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _loading ? null : _goToCreatedGame,
              icon: const Icon(Icons.play_arrow),
              label: const Text('Go to Game Lobby'),
              style: _greenButtonStyle(),
            ),
          ] else ...[
            Text(
              'Start a new game and share the room code with a friend.',
              style: TextStyle(color: kTextSecondary, fontSize: 13),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _loading ? null : _createGame,
              icon: const Icon(Icons.add),
              label: const Text('Create New Game'),
              style: _accentButtonStyle(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildRoomCodeDisplay() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: kCardBg,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: kGrassColor.withAlpha(100)),
      ),
      child: Row(
        children: [
          const Text('🔑', style: TextStyle(fontSize: 20)),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Room Code',
                  style: TextStyle(color: kTextSecondary, fontSize: 11),
                ),
                Text(
                  _createdRoomCode!,
                  style: const TextStyle(
                    color: kGrassColor,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 2,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.copy, color: kTextSecondary, size: 20),
            tooltip: 'Copy',
            onPressed: () {
              Clipboard.setData(ClipboardData(text: _createdRoomCode!));
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Room code copied!'),
                  duration: Duration(seconds: 1),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildDivider() {
    return Row(
      children: [
        Expanded(child: Divider(color: Colors.white12)),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          child: Text('OR', style: TextStyle(color: kTextSecondary, fontSize: 12)),
        ),
        Expanded(child: Divider(color: Colors.white12)),
      ],
    );
  }

  Widget _buildJoinSection() {
    return _Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const _SectionTitle(icon: '🔗', title: 'Join Game'),
          const SizedBox(height: 16),
          TextField(
            controller: _joinCodeCtrl,
            style: const TextStyle(
              color: kTextPrimary,
              letterSpacing: 2,
              fontWeight: FontWeight.bold,
            ),
            decoration: InputDecoration(
              hintText: 'Enter room code',
              hintStyle: TextStyle(color: kTextSecondary, letterSpacing: 0),
              prefixIcon:
                  const Icon(Icons.vpn_key_outlined, color: kTextSecondary),
              filled: true,
              fillColor: kCardBg,
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Colors.white12),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide:
                    const BorderSide(color: kWaterColor, width: 1.5),
              ),
            ),
            textCapitalization: TextCapitalization.none,
            onSubmitted: (_) => _joinGame(),
          ),
          const SizedBox(height: 14),
          ElevatedButton.icon(
            onPressed: _loading ? null : _joinGame,
            icon: const Icon(Icons.login),
            label: const Text('Join Game'),
            style: _blueButtonStyle(),
          ),
        ],
      ),
    );
  }

  ButtonStyle _accentButtonStyle() => ElevatedButton.styleFrom(
        backgroundColor: kAccent,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      );

  ButtonStyle _greenButtonStyle() => ElevatedButton.styleFrom(
        backgroundColor: kGrassColor,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      );

  ButtonStyle _blueButtonStyle() => ElevatedButton.styleFrom(
        backgroundColor: kWaterColor,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      );
}

class _Card extends StatelessWidget {
  final Widget child;
  const _Card({required this.child});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: kSurface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: child,
    );
  }
}

class _SectionTitle extends StatelessWidget {
  final String icon;
  final String title;
  const _SectionTitle({required this.icon, required this.title});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(icon, style: const TextStyle(fontSize: 20)),
        const SizedBox(width: 10),
        Text(
          title,
          style: const TextStyle(
            color: kTextPrimary,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
}
