import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:hacknation_app/pages/SizesPage.dart';
import 'package:hacknation_app/pages/PaymentPage.dart';

/// Opens the profile sheet as a modal bottom sheet (like the ChatGPT settings).
void showProfileSheet(BuildContext context) {
  showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (_) => const ProfilePage(),
  );
}

class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    final topPadding = MediaQuery.of(context).padding.top;

    return Container(
      height: MediaQuery.of(context).size.height * 0.75,
      decoration: const BoxDecoration(
        color: Color(0xFFF7F7F8),
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        children: [
          // ── Header ──
          Padding(
            padding: const EdgeInsets.only(top: 16, left: 8, right: 8),
            child: Row(
              children: [
                const SizedBox(width: 48),
                const Expanded(
                  child: Text(
                    'Einstellungen',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: Colors.black,
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(CupertinoIcons.xmark, size: 20),
                  onPressed: () => Navigator.pop(context),
                ),
              ],
            ),
          ),

          // ── Scrollable content ──
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  const SizedBox(height: 15),

                  // ── Section: Konto ──
                  const Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Konto',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                        color: Colors.grey,
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),

                  _SettingsCard(
                    children: [
                      _SettingsTile(
                        icon: Icons.straighten,
                        title: 'Größen',
                        hasChevron: true,
                        onTap: () {
                          Navigator.pop(context);
                          showSizesSheet(context);
                        },
                      ),
                      _SettingsTile(
                        icon: CupertinoIcons.bag,
                        title: 'Meine Bestellungen',
                        hasChevron: true,
                      ),
                      _SettingsTile(
                        icon: CupertinoIcons.creditcard,
                        title: 'Zahlungsarten',
                        hasChevron: true,
                        onTap: () {
                          Navigator.pop(context);
                          showPaymentSheet(context);
                        },
                      ),
                    ],
                  ),

                  const SizedBox(height: 28),

                  // ── Section: Allgemein ──
                  const Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Allgemein',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                        color: Colors.grey,
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),

                  _SettingsCard(
                    children: [
                      _SettingsTile(
                        icon: CupertinoIcons.slider_horizontal_3,
                        title: 'Personalisierung',
                        hasChevron: true,
                      ),
                      _SettingsTile(
                        icon: CupertinoIcons.bell,
                        title: 'Benachrichtigungen',
                        hasChevron: true,
                      ),
                      _SettingsTile(
                        icon: CupertinoIcons.question_circle,
                        title: 'Hilfe & Support',
                        hasChevron: true,
                      ),
                    ],
                  ),

                  const SizedBox(height: 28),

                  // Log-out
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      onPressed: () {
                        Navigator.pop(context);
                        // TODO: logout logic
                      },
                      icon: const Icon(
                        CupertinoIcons.square_arrow_right,
                        size: 18,
                      ),
                      label: const Text('Abmelden'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.red,
                        side: const BorderSide(color: Colors.red),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(20),
                        ),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                      ),
                    ),
                  ),
                  const SizedBox(height: 32),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Rounded card that wraps a group of tiles ──
class _SettingsCard extends StatelessWidget {
  final List<_SettingsTile> children;
  const _SettingsCard({required this.children});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        children: [
          for (int i = 0; i < children.length; i++) ...[
            children[i],
            if (i < children.length - 1)
              const Divider(height: 1, indent: 54, endIndent: 16),
          ],
        ],
      ),
    );
  }
}

// ── Single settings row ──
class _SettingsTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? subtitle;
  final String? trailing;
  final bool hasChevron;
  final VoidCallback? onTap;

  const _SettingsTile({
    required this.icon,
    required this.title,
    this.subtitle,
    this.trailing,
    this.hasChevron = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Row(
          children: [
            Icon(icon, size: 22, color: Colors.black87),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(fontSize: 16, color: Colors.black),
                  ),
                  if (subtitle != null) ...[
                    const SizedBox(height: 2),
                    Text(
                      subtitle!,
                      style: const TextStyle(fontSize: 13, color: Colors.grey),
                    ),
                  ],
                ],
              ),
            ),
            if (trailing != null)
              Text(
                trailing!,
                style: const TextStyle(fontSize: 14, color: Colors.grey),
              ),
            if (hasChevron)
              const Icon(
                CupertinoIcons.chevron_right,
                size: 16,
                color: Colors.grey,
              ),
          ],
        ),
      ),
    );
  }
}
