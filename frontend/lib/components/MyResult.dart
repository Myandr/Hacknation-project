import 'package:flutter/material.dart';

class MyResult extends StatelessWidget {
  MyResult({super.key, required this.price, required this.name});

  final String name;

  final String price;

  @override
  Widget build(BuildContext context) {
    return Container(
            width: double.infinity,
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.06),
                  blurRadius: 10,
                  spreadRadius: 2,
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: Container(
                    height: 80,
                    decoration: BoxDecoration(
                      color: Colors.red,
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                ),
                Expanded(
                  child: SizedBox(
                    child: Column(
                      children: [
                        Text(name,
                            style: TextStyle(
                                fontSize: 18, fontWeight: FontWeight.bold),),
                        Text(price,
                            style: TextStyle(
                                fontSize: 16, color: Colors.grey.shade600))
                      ],
                    ),
                  )
                  )
              ],
            ),
          );
  }
}