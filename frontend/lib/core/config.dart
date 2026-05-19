import 'package:flutter/material.dart';

// In Docker the Nginx proxy sits in front, so BASE_URL is empty (relative paths).
// When running via `flutter run` locally the defaults point straight at the backend.
const String kBaseUrl =
    String.fromEnvironment('BASE_URL', defaultValue: 'http://127.0.0.1:8000');
const String kWsBaseUrl =
    String.fromEnvironment('WS_BASE_URL', defaultValue: 'ws://127.0.0.1:8000');

// Element colours
const Color kFireColor = Color(0xFFFF6B35);
const Color kWaterColor = Color(0xFF4FC3F7);
const Color kGrassColor = Color(0xFF66BB6A);

// App palette
const Color kBgDark = Color(0xFF0F0F1E);
const Color kSurface = Color(0xFF1A1A2E);
const Color kCardBg = Color(0xFF16213E);
const Color kAccent = Color(0xFFE040FB);
const Color kTextPrimary = Color(0xFFEEEEEE);
const Color kTextSecondary = Color(0xFF9E9E9E);

Color elementColor(String element) {
  switch (element.toLowerCase()) {
    case 'fire':
      return kFireColor;
    case 'water':
      return kWaterColor;
    case 'grass':
      return kGrassColor;
    default:
      return kTextSecondary;
  }
}

String elementEmoji(String element) {
  switch (element.toLowerCase()) {
    case 'fire':
      return '🔥';
    case 'water':
      return '💧';
    case 'grass':
      return '🌿';
    default:
      return '?';
  }
}
