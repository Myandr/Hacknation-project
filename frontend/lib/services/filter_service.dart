import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:hacknation_app/services/create_session.dart' show baseUrl;

/// Datenmodell für Filter Request
class FilterRequest {
  final String? gender;
  final String? sizeClothing;
  final String? sizePants;
  final String? sizeShoes;
  final double? priceMin;
  final double? priceMax;
  final String? color;
  final int? deliveryTimeDays;

  FilterRequest({
    this.gender,
    this.sizeClothing,
    this.sizePants,
    this.sizeShoes,
    this.priceMin,
    this.priceMax,
    this.color,
    this.deliveryTimeDays,
  });

  Map<String, dynamic> toJson() {
    return {
      if (gender != null) 'gender': gender,
      if (sizeClothing != null) 'size_clothing': sizeClothing,
      if (sizePants != null) 'size_pants': sizePants,
      if (sizeShoes != null) 'size_shoes': sizeShoes,
      if (priceMin != null) 'price_min': priceMin,
      if (priceMax != null) 'price_max': priceMax,
      if (color != null) 'color': color,
      if (deliveryTimeDays != null) 'delivery_time_days': deliveryTimeDays,
    };
  }
}

/// Datenmodell für Filter Response
class FilterData {
  final String? gender;
  final String? sizeClothing;
  final String? sizePants;
  final String? sizeShoes;
  final double? priceMin;
  final double? priceMax;
  final String? color;
  final int? deliveryTimeDays;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  FilterData({
    this.gender,
    this.sizeClothing,
    this.sizePants,
    this.sizeShoes,
    this.priceMin,
    this.priceMax,
    this.color,
    this.deliveryTimeDays,
    this.createdAt,
    this.updatedAt,
  });

  factory FilterData.fromJson(Map<String, dynamic> json) {
    return FilterData(
      gender: json['gender'] as String?,
      sizeClothing: json['size_clothing'] as String?,
      sizePants: json['size_pants'] as String?,
      sizeShoes: json['size_shoes'] as String?,
      priceMin: json['price_min'] != null
          ? (json['price_min'] as num).toDouble()
          : null,
      priceMax: json['price_max'] != null
          ? (json['price_max'] as num).toDouble()
          : null,
      color: json['color'] as String?,
      deliveryTimeDays: json['delivery_time_days'] as int?,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : null,
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'])
          : null,
    );
  }
}

/// Ruft die gespeicherten Filter ab
Future<FilterData> getFilters() async {
  final url = Uri.parse('$baseUrl/filters');

  final response = await http.get(url);

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    return FilterData.fromJson(data);
  } else {
    throw Exception(
      'Filter konnten nicht abgerufen werden: ${response.statusCode}',
    );
  }
}

/// Speichert Filter am Backend
Future<FilterData> saveFilters(FilterRequest request) async {
  final url = Uri.parse('$baseUrl/filters');

  final response = await http.post(
    url,
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode(request.toJson()),
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    return FilterData.fromJson(data);
  } else {
    throw Exception(
      'Filter konnten nicht gespeichert werden: ${response.statusCode} - ${response.body}',
    );
  }
}
