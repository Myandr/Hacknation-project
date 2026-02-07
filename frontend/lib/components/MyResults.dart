import 'package:flutter/material.dart';
import 'package:hacknation_app/components/MyResult.dart';

class MyResults extends StatelessWidget {
  const MyResults({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 20, right: 20, top: 12),
          child: MyResult(price: '450€', name: 'Moncler Maya',),
        ),
      ],
    );
  }
}
