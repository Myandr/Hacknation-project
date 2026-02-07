import 'dart:ui';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class MyQuestionTile extends StatefulWidget {
  final String question;
  final String? answer;
  final VoidCallback? onTap;
  final ValueChanged<String>? onAnswerSubmitted;

  const MyQuestionTile({
    super.key,
    this.question = 'Wieviele Leute sollen kommen?',
    this.answer,
    this.onTap,
    this.onAnswerSubmitted,
  });

  @override
  State<MyQuestionTile> createState() => _MyQuestionTileState();
}

class _MyQuestionTileState extends State<MyQuestionTile> {
  bool _isExpanded = false;
  final TextEditingController _answerController = TextEditingController();

  bool get _hasAnswer => widget.answer != null && widget.answer!.isNotEmpty;

  @override
  void dispose() {
    _answerController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Stack(
          alignment: Alignment.center,
          children: [
            // Question text with arrow icon
            Row(
              children: [
                Flexible(
                  child: Text(
                    widget.question,
                    style: const TextStyle(fontSize: 18, color: Colors.black),
                  ),
                ),
                const SizedBox(width: 8),
                GestureDetector(
                  onTap: () {
                    setState(() {
                      _isExpanded = !_isExpanded;
                    });
                  },
                  child: AnimatedRotation(
                    turns: _isExpanded ? 0.25 : 0,
                    duration: const Duration(milliseconds: 200),
                    child: const Icon(
                      CupertinoIcons.right_chevron,
                      color: Colors.black,
                      size: 20,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
        // Answer text field
        AnimatedSize(
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeInOut,
          child: _isExpanded
              ? Padding(
                  padding: const EdgeInsets.only(left: 20, right: 20, top: 12),
                  child: _hasAnswer
                      ? Container(
                          width: double.infinity,
                          padding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 12,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.grey.shade50,
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Text(
                            widget.answer!,
                            style: const TextStyle(
                              fontSize: 15,
                              color: Colors.black87,
                            ),
                          ),
                        )
                      : Container(
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(16),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.05),
                                blurRadius: 10,
                                spreadRadius: 2,
                              ),
                            ],
                          ),
                          child: Row(
                            children: [
                              Expanded(
                                child: TextField(
                                  controller: _answerController,
                                  style: const TextStyle(
                                    fontSize: 15,
                                    color: Colors.black87,
                                  ),
                                  decoration: InputDecoration(
                                    hintText: 'Deine Antwort...',
                                    hintStyle: TextStyle(
                                      color: Colors.grey.shade400,
                                      fontSize: 15,
                                    ),
                                    border: InputBorder.none,
                                    isDense: true,
                                    contentPadding: const EdgeInsets.symmetric(
                                      horizontal: 16,
                                      vertical: 12,
                                    ),
                                  ),
                                ),
                              ),
                              GestureDetector(
                                onTap: () {
                                  final text = _answerController.text.trim();
                                  if (text.isNotEmpty) {
                                    widget.onAnswerSubmitted?.call(text);
                                    _answerController.clear();
                                  }
                                },
                                child: Padding(
                                  padding: const EdgeInsets.only(right: 16),
                                  child: Icon(
                                    CupertinoIcons.paperplane,
                                    color: Colors.grey.shade400,
                                    size: 20,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                )
              : const SizedBox.shrink(),
        ),
      ],
    );
  }
}
