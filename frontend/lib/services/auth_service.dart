import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../core/config.dart';
import '../core/storage.dart';

class AuthService extends ChangeNotifier {
  String? _token;
  String? _username;

  String? get token => _token;
  String? get username => _username;
  bool get isLoggedIn => _token != null;

  Future<void> loadFromStorage() async {
    _token = await Storage.getToken();
    _username = await Storage.getUsername();
    notifyListeners();
  }

  Future<void> register(String username, String email, String password) async {
    final res = await http.post(
      Uri.parse('$kBaseUrl/api/v1/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'email': email,
        'password': password,
      }),
    );
    if (res.statusCode != 200) {
      final body = jsonDecode(res.body);
      throw Exception(body['detail'] ?? 'Registration failed');
    }
  }

  Future<void> login(String username, String password) async {
    final res = await http.post(
      Uri.parse('$kBaseUrl/api/v1/auth/token'),
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: 'username=${Uri.encodeComponent(username)}&password=${Uri.encodeComponent(password)}',
    );
    if (res.statusCode != 200) {
      final body = jsonDecode(res.body);
      throw Exception(body['detail'] ?? 'Login failed');
    }
    final body = jsonDecode(res.body);
    _token = body['access_token'] as String;
    _username = username;
    await Storage.saveToken(_token!);
    await Storage.saveUsername(_username!);
    notifyListeners();
  }

  Future<void> logout() async {
    _token = null;
    _username = null;
    await Storage.clear();
    notifyListeners();
  }
}
