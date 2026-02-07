import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:hacknation_app/components/MyResults.dart';
import 'package:hacknation_app/components/MyTextField.dart';
import 'package:hacknation_app/models/product_item.dart';
import 'package:hacknation_app/services/api_service.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String? _sessionId;
  final List<ChatMessage> _messages = [];
  List<ProductItem> _products = [];
  bool _isLoading = false;
  final TextEditingController _textController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _createSession();
  }

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  Future<void> _createSession() async {
    final sessionId = await ApiService.createSession();
    if (sessionId != null && mounted) {
      setState(() => _sessionId = sessionId);
    }
  }

  Future<void> _sendMessage() async {
    final text = _textController.text.trim();
    if (text.isEmpty || _sessionId == null || _isLoading) return;

    setState(() {
      _messages.add(ChatMessage(role: 'user', content: text));
      _textController.clear();
      _isLoading = true;
    });

    final response = await ApiService.sendMessage(_sessionId!, text);

    if (!mounted) return;
    setState(() => _isLoading = false);

    if (response == null) {
      setState(() {
        _messages.add(ChatMessage(
          role: 'assistant',
          content: 'Verbindung zum Server fehlgeschlagen. Bitte später erneut versuchen.',
        ));
      });
      return;
    }

    setState(() {
      _messages.add(ChatMessage(role: 'assistant', content: response.reply));
      if (response.status == 'ready_for_search') {
        if (response.products.isNotEmpty) {
          _products = response.products;
        } else {
          _loadProductsFallback();
        }
      }
    });
  }

  Future<void> _loadProductsFallback() async {
    if (_sessionId == null) return;
    final products = await ApiService.fetchProducts(_sessionId!);
    if (mounted) setState(() => _products = products);
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
          onPressed: () {},
        ),
        title: const Text(
          'Ski Outfit',
          style: TextStyle(color: Colors.black),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(CupertinoIcons.shopping_cart, color: Colors.black),
            onPressed: () {},
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.only(left: 12, right: 12, bottom: 32, top: 12),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            Expanded(
              child: Align(
                alignment: Alignment.topLeft,
                child: _sessionId == null
                    ? const Center(child: CircularProgressIndicator())
                    : MyResults(
                        messages: _messages,
                        products: _products,
                        isLoading: _isLoading,
                      ),
              ),
            ),
            MyTextField(
              controller: _textController,
              hintText: 'Schreib deine Antwort...',
              onSend: _sendMessage,
            ),
          ],
        ),
      ),
    );
  }
}
