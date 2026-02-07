import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Drawer(
      backgroundColor: Colors.white,
      child: SafeArea(
        child: Column(
          children: [
            const SizedBox(height: 24),
            // Avatar & Name
            const CircleAvatar(
              radius: 45,
              backgroundColor: Color(0xFFE0E0E0),
              child: Icon(
                CupertinoIcons.person_fill,
                size: 45,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'Gast',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            const Text(
              'Nicht angemeldet',
              style: TextStyle(fontSize: 14, color: Colors.grey),
            ),
            const SizedBox(height: 24),
            const Divider(),

            // Menu items
            _ProfileMenuItem(
              icon: CupertinoIcons.person,
              title: 'Mein Profil',
              onTap: () {
                Navigator.pop(context);
                // TODO: Navigate to profile details
              },
            ),
            _ProfileMenuItem(
              icon: CupertinoIcons.bag,
              title: 'Meine Bestellungen',
              onTap: () {
                Navigator.pop(context);
                // TODO: Navigate to orders
              },
            ),
            _ProfileMenuItem(
              icon: CupertinoIcons.heart,
              title: 'Wunschliste',
              onTap: () {
                Navigator.pop(context);
                // TODO: Navigate to wishlist
              },
            ),
            _ProfileMenuItem(
              icon: CupertinoIcons.settings,
              title: 'Einstellungen',
              onTap: () {
                Navigator.pop(context);
                // TODO: Navigate to settings
              },
            ),
            _ProfileMenuItem(
              icon: CupertinoIcons.question_circle,
              title: 'Hilfe & Support',
              onTap: () {
                Navigator.pop(context);
                // TODO: Navigate to help
              },
            ),

            const Spacer(),
            const Divider(),
            _ProfileMenuItem(
              icon: CupertinoIcons.square_arrow_right,
              title: 'Anmelden',
              onTap: () {
                Navigator.pop(context);
                // TODO: Login/Logout logic
              },
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}

class _ProfileMenuItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final VoidCallback? onTap;

  const _ProfileMenuItem({required this.icon, required this.title, this.onTap});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: Colors.black87),
      title: Text(title, style: const TextStyle(fontSize: 16)),
      trailing: const Icon(Icons.chevron_right, color: Colors.grey),
      onTap: onTap,
    );
  }
}
