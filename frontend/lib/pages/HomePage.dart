import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:hacknation_app/components/MyQuestionTile.dart';
import 'package:hacknation_app/components/MyTextField.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

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
          'Hackathon Planung',
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
            const Align(
              alignment: Alignment.centerLeft,
              child: MyQuestionTile(),
            ),
            const Spacer(),
            MyTextField(),
          ],
        ),
      ),
    );
  }
}
