import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:hacknation_app/components/MyQuestionTile.dart';
import 'package:hacknation_app/components/MyTextField.dart';
import 'package:hacknation_app/services/create_session.dart';
import 'package:hacknation_app/pages/ProfilePage.dart';
import 'package:hacknation_app/services/send_message.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();
  String? sessionId;
  bool isLoading = true;
  String? error;

  final TextEditingController _messageController = TextEditingController();
  final List<Map<String, String>> _messages = []; // {role, content}
  bool _isSending = false;

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
        _isSending = false;
      });
    } catch (e) {
      setState(() {
        _messages.add({'role': 'assistant', 'content': 'Fehler: $e'});
        _isSending = false;
      });
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

  /// Gibt true zurück, wenn es noch keine KI-Frage gibt (erster Schritt).
  bool get _showBottomTextField => _questionAnswerPairs.isEmpty && !_isSending;

  @override
  void dispose() {
    _messageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      backgroundColor: Colors.white,
      drawer: const ProfilePage(),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(CupertinoIcons.person, color: Colors.black),
          onPressed: () => _scaffoldKey.currentState?.openDrawer(),
        ),
        title: const Text('Ski Outfit', style: TextStyle(color: Colors.black)),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(CupertinoIcons.shopping_cart, color: Colors.black),
            onPressed: () {},
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
                  : ListView.builder(
                      padding: const EdgeInsets.only(top: 8),
                      itemCount:
                          _questionAnswerPairs.length + (_isSending ? 1 : 0),
                      itemBuilder: (context, index) {
                        if (index == _questionAnswerPairs.length) {
                          return const Align(
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
                          );
                        }
                        final pair = _questionAnswerPairs[index];
                        final isLast = index == _questionAnswerPairs.length - 1;
                        final hasNoAnswer = pair['answer'] == null;
                        return Padding(
                          padding: const EdgeInsets.symmetric(vertical: 6),
                          child: MyQuestionTile(
                            question: pair['question']!,
                            answer: pair['answer'],
                            onAnswerSubmitted: (isLast && hasNoAnswer)
                                ? _sendMessage
                                : null,
                          ),
                        );
                      },
                    ),
            ),
            MyTextField(
              controller: _messageController,
              onSend: _sendMessage,
              enabled: _showBottomTextField,
            ),
          ],
        ),
      ),
    );
  }
}
