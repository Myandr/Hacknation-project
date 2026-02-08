import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:hacknation_app/services/filter_service.dart';

/// Opens the sizes sheet as a modal bottom sheet (same style as ProfilePage).
void showSizesSheet(BuildContext context) {
  showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (_) => const SizesPage(),
  );
}

class SizesPage extends StatefulWidget {
  const SizesPage({super.key});

  @override
  State<SizesPage> createState() => _SizesPageState();
}

class _SizesPageState extends State<SizesPage> {
  // Current selections
  String? _tshirtSize;
  String? _pantsSize;
  String? _shoeSize;
  String _gender = 'male'; // 'male' or 'female'
  bool _isLoading = true;
  bool _isSaving = false;

  // Available options
  static const _tshirtSizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL'];
  static const _pantsSizes = ['26', '28', '30', '32', '34', '36', '38', '40'];
  static const _shoeSizes = [
    '36',
    '37',
    '38',
    '39',
    '40',
    '41',
    '42',
    '43',
    '44',
    '45',
    '46',
  ];

  @override
  void initState() {
    super.initState();
    _loadFilters();
  }

  Future<void> _loadFilters() async {
    try {
      final filters = await getFilters();
      setState(() {
        _gender = filters.gender ?? 'male';
        _tshirtSize = filters.sizeClothing;
        _pantsSize = filters.sizePants;
        _shoeSize = filters.sizeShoes;
        _isLoading = false;
      });
    } catch (e) {
      debugPrint('Fehler beim Laden der Filter: $e');
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _saveFilters() async {
    if (_isSaving) return;

    setState(() {
      _isSaving = true;
    });

    try {
      final request = FilterRequest(
        gender: _gender,
        sizeClothing: _tshirtSize,
        sizePants: _pantsSize,
        sizeShoes: _shoeSize,
      );
      await saveFilters(request);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Größen gespeichert'),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 2),
          ),
        );
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Fehler: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSaving = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
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
            padding: const EdgeInsets.only(top: 16, left: 12, right: 12),
            child: Row(
              children: [
                IconButton(
                  icon: const Icon(CupertinoIcons.chevron_back, size: 20),
                  onPressed: () => Navigator.pop(context),
                ),
                const Expanded(
                  child: Text(
                    'Meine Größen',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: Colors.black,
                    ),
                  ),
                ),
                const SizedBox(width: 48),
              ],
            ),
          ),

          // ── Content ──
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : SingleChildScrollView(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 20),

                        // Geschlecht
                        const Row(
                          children: [
                            Icon(Icons.person, size: 20, color: Colors.black87),
                            SizedBox(width: 10),
                            Text(
                              'Geschlecht',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                                color: Colors.black,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Row(
                            children: [
                              Expanded(
                                child: GestureDetector(
                                  onTap: () => setState(() => _gender = 'male'),
                                  child: AnimatedContainer(
                                    duration: const Duration(milliseconds: 200),
                                    padding: const EdgeInsets.symmetric(
                                      vertical: 12,
                                    ),
                                    decoration: BoxDecoration(
                                      color: _gender == 'male'
                                          ? Colors.black
                                          : const Color(0xFFF0F0F0),
                                      borderRadius: BorderRadius.circular(14),
                                    ),
                                    child: Text(
                                      'Männlich',
                                      textAlign: TextAlign.center,
                                      style: TextStyle(
                                        fontSize: 14,
                                        fontWeight: FontWeight.w500,
                                        color: _gender == 'male'
                                            ? Colors.white
                                            : Colors.black87,
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(width: 10),
                              Expanded(
                                child: GestureDetector(
                                  onTap: () =>
                                      setState(() => _gender = 'female'),
                                  child: AnimatedContainer(
                                    duration: const Duration(milliseconds: 200),
                                    padding: const EdgeInsets.symmetric(
                                      vertical: 12,
                                    ),
                                    decoration: BoxDecoration(
                                      color: _gender == 'female'
                                          ? Colors.black
                                          : const Color(0xFFF0F0F0),
                                      borderRadius: BorderRadius.circular(14),
                                    ),
                                    child: Text(
                                      'Weiblich',
                                      textAlign: TextAlign.center,
                                      style: TextStyle(
                                        fontSize: 14,
                                        fontWeight: FontWeight.w500,
                                        color: _gender == 'female'
                                            ? Colors.white
                                            : Colors.black87,
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),

                        const SizedBox(height: 24),

                        // T-Shirt
                        _SizeSection(
                          icon: Icons.checkroom,
                          title: 'T-Shirt',
                          sizes: _tshirtSizes,
                          selectedSize: _tshirtSize,
                          onSelected: (size) =>
                              setState(() => _tshirtSize = size),
                        ),

                        const SizedBox(height: 24),

                        // Hose
                        _SizeSection(
                          icon: Icons.accessibility_new,
                          title: 'Hose',
                          sizes: _pantsSizes,
                          selectedSize: _pantsSize,
                          onSelected: (size) =>
                              setState(() => _pantsSize = size),
                        ),

                        const SizedBox(height: 24),

                        // Schuhe
                        _SizeSection(
                          icon: CupertinoIcons.sportscourt,
                          title: 'Schuhe',
                          sizes: _shoeSizes,
                          selectedSize: _shoeSize,
                          onSelected: (size) =>
                              setState(() => _shoeSize = size),
                        ),

                        const SizedBox(height: 32),

                        // Save button
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: _isSaving ? null : _saveFilters,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.black,
                              foregroundColor: Colors.white,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(20),
                              ),
                              padding: const EdgeInsets.symmetric(vertical: 14),
                            ),
                            child: _isSaving
                                ? const SizedBox(
                                    height: 20,
                                    width: 20,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      valueColor: AlwaysStoppedAnimation<Color>(
                                        Colors.white,
                                      ),
                                    ),
                                  )
                                : const Text(
                                    'Speichern',
                                    style: TextStyle(fontSize: 16),
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

/// A section with a label and a row of selectable size chips.
class _SizeSection extends StatelessWidget {
  final IconData icon;
  final String title;
  final List<String> sizes;
  final String? selectedSize;
  final ValueChanged<String> onSelected;

  const _SizeSection({
    required this.icon,
    required this.title,
    required this.sizes,
    required this.selectedSize,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Section header
        Row(
          children: [
            Icon(icon, size: 20, color: Colors.black87),
            const SizedBox(width: 10),
            Text(
              title,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Colors.black,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        // Size chips in a white card
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Wrap(
            spacing: 10,
            runSpacing: 10,
            children: sizes.map((size) {
              final isSelected = size == selectedSize;
              return GestureDetector(
                onTap: () => onSelected(size),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  padding: const EdgeInsets.symmetric(
                    horizontal: 18,
                    vertical: 10,
                  ),
                  decoration: BoxDecoration(
                    color: isSelected ? Colors.black : const Color(0xFFF0F0F0),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: Text(
                    size,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      color: isSelected ? Colors.white : Colors.black87,
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }
}
