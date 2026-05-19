import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/config.dart';
import 'services/auth_service.dart';
import 'screens/login_screen.dart';
import 'screens/lobby_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final auth = AuthService();
  await auth.loadFromStorage();

  runApp(
    ChangeNotifierProvider.value(
      value: auth,
      child: const ElementalCircleApp(),
    ),
  );
}

class ElementalCircleApp extends StatelessWidget {
  const ElementalCircleApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Elemental Circle',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.dark(
          primary: kAccent,
          surface: kSurface,
        ),
        scaffoldBackgroundColor: kBgDark,
        useMaterial3: true,
      ),
      home: context.watch<AuthService>().isLoggedIn
          ? const LobbyScreen()
          : const LoginScreen(),
    );
  }
}
