import 'package:flutter/material.dart';
import '../core/config.dart';
import '../models/card_model.dart';

class CardWidget extends StatelessWidget {
  final CardModel card;
  final bool isPlayable;
  final bool isSelected;
  final VoidCallback? onTap;

  const CardWidget({
    super.key,
    required this.card,
    this.isPlayable = false,
    this.isSelected = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final color = elementColor(card.element);

    return GestureDetector(
      onTap: isPlayable ? onTap : null,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        width: 72,
        height: 100,
        transform: isSelected
            ? (Matrix4.identity()..translate(0.0, -12.0))
            : Matrix4.identity(),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? color : color.withAlpha(120),
            width: isSelected ? 2.5 : 1.5,
          ),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              kCardBg,
              color.withAlpha(40),
            ],
          ),
          boxShadow: isSelected
              ? [BoxShadow(color: color.withAlpha(100), blurRadius: 14, spreadRadius: 2)]
              : [BoxShadow(color: Colors.black45, blurRadius: 4)],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              elementEmoji(card.element),
              style: const TextStyle(fontSize: 22),
            ),
            const SizedBox(height: 6),
            Text(
              '${card.value}',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              card.element.toUpperCase(),
              style: TextStyle(
                fontSize: 9,
                letterSpacing: 1.2,
                color: color.withAlpha(200),
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class BoardCard extends StatelessWidget {
  final CardModel? card;

  const BoardCard({super.key, this.card});

  @override
  Widget build(BuildContext context) {
    if (card == null) {
      return Container(
        width: 110,
        height: 154,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.white12, width: 2),
          color: kCardBg,
        ),
        child: const Center(
          child: Text('?', style: TextStyle(color: Colors.white24, fontSize: 36)),
        ),
      );
    }

    final color = elementColor(card!.element);
    return Container(
      width: 110,
      height: 154,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withAlpha(180), width: 2.5),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [kCardBg, color.withAlpha(60)],
        ),
        boxShadow: [
          BoxShadow(color: color.withAlpha(80), blurRadius: 20, spreadRadius: 2),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(elementEmoji(card!.element), style: const TextStyle(fontSize: 32)),
          const SizedBox(height: 8),
          Text(
            '${card!.value}',
            style: TextStyle(
              fontSize: 42,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            card!.element.toUpperCase(),
            style: TextStyle(
              fontSize: 11,
              letterSpacing: 1.5,
              color: color.withAlpha(200),
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}
