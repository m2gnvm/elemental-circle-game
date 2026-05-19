class CardModel {
  final int value;
  final String element;

  const CardModel({required this.value, required this.element});

  factory CardModel.fromJson(Map<String, dynamic> json) => CardModel(
        value: (json['value'] as num).toInt(),
        element: json['element'] as String,
      );

  Map<String, dynamic> toJson() => {'value': value, 'element': element};

  @override
  String toString() => 'Card($value, $element)';
}
