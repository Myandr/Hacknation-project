import 'dart:io';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:hacknation_app/components/MyQuestionTile.dart';
import 'package:hacknation_app/components/MyResults.dart';
import 'package:hacknation_app/components/MyTextField.dart';
import 'package:hacknation_app/services/create_session.dart';
import 'package:hacknation_app/pages/ProfilePage.dart';
import 'package:hacknation_app/pages/CartPage.dart';
import 'package:hacknation_app/services/send_message.dart';
import 'package:hacknation_app/services/search_products.dart';
import 'package:hacknation_app/services/cart_service.dart';
import 'package:hacknation_app/services/shopping_plan_service.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String? sessionId;
  bool isLoading = true;
  String? error;

  final TextEditingController _messageController = TextEditingController();
  final List<Map<String, String>> _messages = []; // {role, content}
  bool _isSending = false;
  String _sessionStatus = 'chatting';

  // Suche
  List<RankedProduct> _searchResults = [];
  bool _isSearching = false;
  String? _searchError;

  // Google Shopping Ergebnisse
  List<PlanComponentSearch> _googleShoppingResults = [];

  // Warenkorb
  final Set<String> _cartProductIds = {};
  int _cartItemCount = 0;

  // File uploads
  final List<File> _selectedFiles = [];

  @override
  void initState() {
    super.initState();
    _initSession();
  }

  Future<void> _initSession() async {
    try {
      final id = await createSession();
      setState(() {
        sessionId = id;
        isLoading = false;
      });
      debugPrint('Session erstellt: $id');
    } catch (e) {
      setState(() {
        error = e.toString();
        isLoading = false;
      });
      debugPrint('Fehler beim Erstellen der Session: $e');
    }
  }

  Future<void> _sendMessage([String? overrideText]) async {
    final text = overrideText ?? _messageController.text.trim();
    if (text.isEmpty || sessionId == null || _isSending) return;

    setState(() {
      _messages.add({'role': 'user', 'content': text});
      if (overrideText == null) _messageController.clear();
      _isSending = true;
    });

    try {
      final response = await sendMessage(sessionId: sessionId!, message: text);
      setState(() {
        _messages.add({'role': 'assistant', 'content': response.reply});
        _sessionStatus = response.status;
        _isSending = false;
      });

      // Automatisch Shopping Plan erstellen und Google Shopping Suche starten wenn Brief vollständig
      if (response.status == 'ready_for_search') {
        await _createShoppingPlanWithGoogleShopping();
      }
    } catch (e) {
      setState(() {
        _messages.add({'role': 'assistant', 'content': 'Fehler: $e'});
        _isSending = false;
      });
    }
  }

  /// Erstellt den Shopping Plan mit Google Shopping Suche.
  Future<void> _createShoppingPlanWithGoogleShopping() async {
    if (sessionId == null || _isSearching) return;

    setState(() {
      _isSearching = true;
      _searchError = null;
    });

    debugPrint('Erstelle Shopping Plan mit Google Shopping...');
    try {
      final results = await createShoppingPlanWithGoogleShopping(
        sessionId: sessionId!,
      );

      // Konvertiere Google Shopping Ergebnisse in RankedProducts für die Anzeige
      final products = convertGoogleShoppingToRankedProducts(results);

      setState(() {
        _googleShoppingResults = results;
        _searchResults = products; // Zeige die Produkte als Suchergebnisse an
        _isSearching = false;
      });

      debugPrint(
        'Shopping Plan mit Google Shopping erstellt: ${results.length} Komponenten, ${products.length} Produkte',
      );
      for (var result in results) {
        debugPrint(
          '  - ${result.component.name}: ${result.shoppingResults.length} Produkte gefunden',
        );
      }
    } catch (e) {
      setState(() {
        _searchError = e.toString();
        _isSearching = false;
      });
      debugPrint('Fehler beim Erstellen des Shopping Plans: $e');
    }
  }

  /// Startet die Multi-Retailer-Suche.
  Future<void> _triggerSearch() async {
    if (sessionId == null || _isSearching) return;

    setState(() {
      _isSearching = true;
      _searchError = null;
    });

    try {
      final result = await searchProducts(sessionId: sessionId!);
      setState(() {
        _searchResults = result.products;
        _isSearching = false;
      });
      debugPrint('Suche abgeschlossen: ${result.products.length} Produkte');
    } catch (e) {
      setState(() {
        _searchError = e.toString();
        _isSearching = false;
      });
      debugPrint('Fehler bei der Suche: $e');
    }
  }

  /// Baut Frage-Antwort-Paare aus der Nachrichtenliste.
  /// Jede Assistant-Nachricht wird zur Frage, die darauffolgende
  /// User-Nachricht (falls vorhanden) wird zur Antwort.
  List<Map<String, String?>> get _questionAnswerPairs {
    final pairs = <Map<String, String?>>[];
    for (int i = 0; i < _messages.length; i++) {
      final msg = _messages[i];
      if (msg['role'] == 'assistant') {
        String? answer;
        // Nächste User-Nachricht als Antwort zuordnen
        if (i + 1 < _messages.length && _messages[i + 1]['role'] == 'user') {
          answer = _messages[i + 1]['content'];
        }
        pairs.add({'question': msg['content']!, 'answer': answer});
      }
    }
    return pairs;
  }

  /// Produkt in den Warenkorb legen.
  Future<void> _addToCart(RankedProduct product) async {
    if (sessionId == null) return;

    try {
      await addToCart(sessionId: sessionId!, product: product);
      setState(() {
        _cartProductIds.add(product.productId);
        _cartItemCount++;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${product.title} in den Warenkorb gelegt'),
            duration: const Duration(seconds: 2),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Fehler: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  /// Öffnet den Warenkorb.
  void _openCart() {
    if (sessionId == null) return;
    showCartSheet(
      context,
      sessionId: sessionId!,
      onCartChanged: _refreshCartCount,
    );
  }

  /// Aktualisiert den Warenkorb-Zähler.
  Future<void> _refreshCartCount() async {
    if (sessionId == null) return;
    try {
      final cart = await getCart(sessionId: sessionId!);
      setState(() {
        _cartItemCount = cart.items.length;
        _cartProductIds.clear();
        for (final item in cart.items) {
          _cartProductIds.add(item.productId);
        }
      });
    } catch (_) {}
  }

  /// Gibt true zurück, wenn es noch keine KI-Frage gibt (erster Schritt).
  bool get _showBottomTextField => _questionAnswerPairs.isEmpty && !_isSending;

  @override
  void dispose() {
    _messageController.dispose();
    super.dispose();
  }

  void _onFilesChanged(List<File> files) {
    setState(() {
      _selectedFiles.clear();
      _selectedFiles.addAll(files);
    });
    // TODO: Handle file upload logic here
    // For now, just print the file names
    print(
      'Selected files: ${files.map((f) => f.path.split('/').last).join(', ')}',
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(CupertinoIcons.person, color: Colors.black),
          onPressed: () => showProfileSheet(context),
        ),
        title: const Text('Ski Outfit', style: TextStyle(color: Colors.black)),
        centerTitle: true,
        actions: [
          Stack(
            children: [
              IconButton(
                icon: const Icon(
                  CupertinoIcons.shopping_cart,
                  color: Colors.black,
                ),
                onPressed: _openCart,
              ),
              if (_cartItemCount > 0)
                Positioned(
                  right: 4,
                  top: 4,
                  child: Container(
                    padding: const EdgeInsets.all(4),
                    decoration: const BoxDecoration(
                      color: Colors.red,
                      shape: BoxShape.circle,
                    ),
                    child: Text(
                      '$_cartItemCount',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.only(
          left: 12,
          right: 12,
          bottom: 32,
          top: 12,
        ),
        child: Column(
          children: [
            Expanded(
              child: _messages.isEmpty
                  ? const Center(
                      child: Text(
                        'Starte eine Unterhaltung!',
                        style: TextStyle(color: Colors.grey),
                      ),
                    )
                  : ListView(
                      padding: const EdgeInsets.only(top: 8),
                      children: [
                        // Chat-Verlauf
                        ..._questionAnswerPairs.asMap().entries.map((entry) {
                          final index = entry.key;
                          final pair = entry.value;
                          final isLast =
                              index == _questionAnswerPairs.length - 1;
                          final hasNoAnswer = pair['answer'] == null;
                          return Padding(
                            padding: const EdgeInsets.symmetric(vertical: 6),
                            child: MyQuestionTile(
                              question: pair['question']!,
                              answer: pair['answer'],
                              onAnswerSubmitted:
                                  (isLast &&
                                      hasNoAnswer &&
                                      !_isSearching &&
                                      _searchResults.isEmpty)
                                  ? _sendMessage
                                  : null,
                            ),
                          );
                        }),
                        // Lade-Indikator (Chat)
                        if (_isSending)
                          const Align(
                            alignment: Alignment.centerLeft,
                            child: Padding(
                              padding: EdgeInsets.all(12),
                              child: SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              ),
                            ),
                          ),
                        // Suche läuft
                        if (_isSearching)
                          const Padding(
                            padding: EdgeInsets.symmetric(vertical: 20),
                            child: Center(
                              child: Column(
                                children: [
                                  CircularProgressIndicator(),
                                  SizedBox(height: 12),
                                  Text(
                                    'Suche läuft...',
                                    style: TextStyle(color: Colors.grey),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        // Suche-Fehler
                        if (_searchError != null)
                          Padding(
                            padding: const EdgeInsets.all(12),
                            child: Text(
                              'Fehler bei der Suche: $_searchError',
                              style: const TextStyle(color: Colors.red),
                            ),
                          ),
                        // Suchergebnisse
                        if (_searchResults.isNotEmpty)
                          Padding(
                            padding: const EdgeInsets.only(top: 12, bottom: 4),
                            child: Text(
                              '${_searchResults.length} Produkte gefunden',
                              style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ),
                        if (_searchResults.isNotEmpty)
                          MyResults(
                            products: _searchResults,
                            onAddToCart: _addToCart,
                            cartProductIds: _cartProductIds,
                          ),
                      ],
                    ),
            ),
            if (_sessionStatus != 'ready_for_search' && _searchResults.isEmpty)
              MyTextField(
                controller: _messageController,
                onSend: _sendMessage,
                onFilesChanged: _onFilesChanged,
                enabled: _showBottomTextField,
              ),
          ],
        ),
      ),
    );
  }
}
