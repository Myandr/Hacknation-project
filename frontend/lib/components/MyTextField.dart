import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'package:file_picker/file_picker.dart';
import 'package:image_picker/image_picker.dart';

class MyTextField extends StatefulWidget {
  final TextEditingController? controller;
  final String hintText;
  final VoidCallback? onSend;
  final ValueChanged<bool>? onModeChanged;
  final ValueChanged<List<File>>? onFilesChanged;
  final bool enabled;

  const MyTextField({
    super.key,
    this.controller,
    this.hintText = 'Ask anything...',
    this.onSend,
    this.onModeChanged,
    this.onFilesChanged,
    this.enabled = true,
  });

  @override
  State<MyTextField> createState() => _MyTextFieldState();
}

class _MyTextFieldState extends State<MyTextField> {
  bool _isChat = true; // true = Chat, false = Upload

  // Filter state
  final TextEditingController _priceFromController = TextEditingController();
  final TextEditingController _priceToController = TextEditingController();
  String _selectedColor = 'Alle Farben';
  String _selectedDelivery = 'Beliebig';
  bool _filterOpen = false;
  OverlayEntry? _filterOverlay;
  final GlobalKey _filterButtonKey = GlobalKey();
  bool _filtersLoaded = false;

  // File upload state
  final List<File> _selectedFiles = [];
  final ImagePicker _imagePicker = ImagePicker();

  static const List<String> _colorOptions = [
    'Alle Farben',
    'Schwarz',
    'Weiß',
    'Rot',
    'Blau',
    'Grün',
    'Gelb',
    'Pink',
    'Grau',
  ];

  static const List<String> _deliveryOptions = [
    'Beliebig',
    '1–3 Tage',
    '3–7 Tage',
    '7–14 Tage',
    '14+ Tage',
  ];

  @override
  void dispose() {
    _priceFromController.dispose();
    _priceToController.dispose();
    _removeFilterOverlay();
    super.dispose();
  }

  void _showFilePickerOptions() {
    if (Platform.isIOS) {
      showCupertinoModalPopup<void>(
        context: context,
        builder: (BuildContext context) => CupertinoActionSheet(
          title: const Text('Datei auswählen'),
          actions: <CupertinoActionSheetAction>[
            CupertinoActionSheetAction(
              onPressed: () {
                Navigator.pop(context);
                _pickImages();
              },
              child: const Text('Fotos aus Mediathek'),
            ),
            CupertinoActionSheetAction(
              onPressed: () {
                Navigator.pop(context);
                _takePhoto();
              },
              child: const Text('Foto aufnehmen'),
            ),
            CupertinoActionSheetAction(
              onPressed: () {
                Navigator.pop(context);
                _pickFiles();
              },
              child: const Text('Dateien auswählen'),
            ),
          ],
          cancelButton: CupertinoActionSheetAction(
            isDestructiveAction: true,
            onPressed: () {
              Navigator.pop(context);
            },
            child: const Text('Abbrechen'),
          ),
        ),
      );
    } else {
      showModalBottomSheet(
        context: context,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        builder: (context) => Container(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.photo_library),
                title: const Text('Fotos aus Galerie'),
                onTap: () {
                  Navigator.pop(context);
                  _pickImages();
                },
              ),
              ListTile(
                leading: const Icon(Icons.camera_alt),
                title: const Text('Foto aufnehmen'),
                onTap: () {
                  Navigator.pop(context);
                  _takePhoto();
                },
              ),
              ListTile(
                leading: const Icon(Icons.attach_file),
                title: const Text('Dateien auswählen'),
                onTap: () {
                  Navigator.pop(context);
                  _pickFiles();
                },
              ),
            ],
          ),
        ),
      );
    }
  }

  Future<void> _pickImages() async {
    try {
      final List<XFile> images = await _imagePicker.pickMultiImage();
      if (images.isNotEmpty) {
        final List<File> newFiles = images
            .map((xFile) => File(xFile.path))
            .toList();
        _addFiles(newFiles);
      }
    } catch (e) {
      _showError('Fehler beim Auswählen der Bilder: $e');
    }
  }

  Future<void> _takePhoto() async {
    try {
      final XFile? photo = await _imagePicker.pickImage(
        source: ImageSource.camera,
      );
      if (photo != null) {
        _addFiles([File(photo.path)]);
      }
    } catch (e) {
      _showError('Fehler beim Aufnehmen des Fotos: $e');
    }
  }

  Future<void> _pickFiles() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        allowMultiple: true,
        type: FileType.custom,
        allowedExtensions: ['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx', 'txt'],
      );

      if (result != null) {
        final List<File> newFiles = result.paths
            .where((path) => path != null)
            .map((path) => File(path!))
            .toList();
        _addFiles(newFiles);
      }
    } catch (e) {
      _showError('Fehler beim Auswählen der Dateien: $e');
    }
  }

  void _addFiles(List<File> newFiles) {
    setState(() {
      _selectedFiles.addAll(newFiles);
    });
    widget.onFilesChanged?.call(_selectedFiles);
  }

  void _removeFile(int index) {
    setState(() {
      _selectedFiles.removeAt(index);
    });
    widget.onFilesChanged?.call(_selectedFiles);
  }

  void _showError(String message) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  void _removeFilterOverlay() {
    _filterOverlay?.remove();
    _filterOverlay = null;
    _filterOpen = false;
  }

  void _handleSend() {
    if (widget.controller == null) {
      widget.onSend?.call();
      return;
    }

    // Hole den aktuellen Text
    String message = widget.controller!.text.trim();

    // Füge Filter hinzu (Preis, Farbe, Lieferzeit)
    List<String> filters = [];

    if (_priceFromController.text.isNotEmpty ||
        _priceToController.text.isNotEmpty) {
      String priceFilter = 'Preis:';
      if (_priceFromController.text.isNotEmpty) {
        priceFilter += ' von ${_priceFromController.text}€';
      }
      if (_priceToController.text.isNotEmpty) {
        priceFilter += ' bis ${_priceToController.text}€';
      }
      filters.add(priceFilter);
    }

    if (_selectedColor != 'Alle Farben') {
      filters.add('Farbe: $_selectedColor');
    }

    if (_selectedDelivery != 'Beliebig') {
      filters.add('Lieferzeit: $_selectedDelivery');
    }

    // Hänge Filter an die Nachricht an
    if (filters.isNotEmpty) {
      message = '$message, ${filters.join(', ')}';
      widget.controller!.text = message;
    }

    // Debug: Zeige den angepassten Prompt
    debugPrint('📝 Angepasster Prompt mit Filtern: $message');

    // Rufe die ursprüngliche onSend-Funktion auf
    widget.onSend?.call();
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // Pink blur glow behind the text field
        Container(
          height: 80,
          margin: const EdgeInsets.symmetric(horizontal: 20),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(40),
            boxShadow: [
              BoxShadow(
                color: Colors.pinkAccent.withOpacity(0.3),
                blurRadius: 80,
                spreadRadius: 20,
              ),
              BoxShadow(
                color: Colors.purpleAccent.withOpacity(0.2),
                blurRadius: 120,
                spreadRadius: 15,
              ),
            ],
          ),
        ),
        // White text field on top
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(28),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // File previews
              if (_selectedFiles.isNotEmpty) ...[
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.only(
                    left: 12,
                    right: 12,
                    top: 8,
                    bottom: 4,
                  ),
                  child: Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: _selectedFiles.asMap().entries.map((entry) {
                      return _FilePreviewChip(
                        file: entry.value,
                        onRemove: () => _removeFile(entry.key),
                      );
                    }).toList(),
                  ),
                ),
                if (_isChat) const Divider(height: 1, color: Color(0xFFE0E0E0)),
              ],
              // Text input area or Upload area
              if (_isChat)
                TextField(
                  controller: widget.controller,
                  enabled: widget.enabled,
                  style: const TextStyle(fontSize: 15, color: Colors.black87),
                  maxLines: null,
                  decoration: InputDecoration(
                    hintText: widget.hintText,
                    hintStyle: TextStyle(
                      color: Colors.grey.shade500,
                      fontSize: 15,
                    ),
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 8,
                    ),
                  ),
                )
              else
                GestureDetector(
                  onTap: _showFilePickerOptions,
                  child: Container(
                    margin: const EdgeInsets.all(8),
                    child: CustomPaint(
                      painter: _DashedBorderPainter(
                        color: Colors.grey.shade400,
                        strokeWidth: 1.5,
                        dashLength: 6,
                        gapLength: 4,
                        borderRadius: 16,
                      ),
                      child: Container(
                        padding: const EdgeInsets.symmetric(vertical: 10),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(16),
                          color: Colors.grey.shade50,
                        ),
                        child: Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                Icons.upload_outlined,
                                size: 28,
                                color: Colors.grey.shade500,
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'Datei auswählen',
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.grey.shade500,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              // Bottom row with buttons
              Row(
                children: [
                  // Manuell / KI Toggle
                  Container(
                    height: 36,
                    padding: const EdgeInsets.all(3),
                    decoration: BoxDecoration(
                      color: Colors.grey.shade200,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        _buildToggleOption('Chat', _isChat),
                        _buildToggleOption('Upload', !_isChat),
                      ],
                    ),
                  ),
                  const Spacer(),
                  // Filter button
                  GestureDetector(
                    key: _filterButtonKey,
                    onTap: _toggleFilterPopup,
                    child: Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        color: Colors.grey.shade100,
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        Icons.tune_rounded,
                        color: Colors.grey.shade700,
                        size: 18,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  // Send button
                  GestureDetector(
                    onTap: widget.enabled ? _handleSend : null,
                    child: Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        color: widget.enabled
                            ? Colors.black
                            : Colors.grey.shade400,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.arrow_upward,
                        color: Colors.white,
                        size: 18,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  void _toggleFilterPopup() async {
    if (_filterOpen) {
      _removeFilterOverlay();
      setState(() {});
      return;
    }

    // Lade Filter beim Öffnen (nur Preis, Farbe, Lieferzeit - nicht speichern)
    if (!_filtersLoaded) {
      _filtersLoaded = true;
    }

    final renderBox =
        _filterButtonKey.currentContext!.findRenderObject() as RenderBox;
    final buttonPos = renderBox.localToGlobal(Offset.zero);
    const popupWidth = 220.0;

    _filterOverlay = OverlayEntry(
      builder: (context) {
        return Stack(
          children: [
            // Tap-away dismiss layer
            Positioned.fill(
              child: GestureDetector(
                behavior: HitTestBehavior.translucent,
                onTap: () {
                  _removeFilterOverlay();
                  setState(() {});
                },
              ),
            ),
            // The small popup card above the button
            Positioned(
              right:
                  MediaQuery.of(context).size.width -
                  buttonPos.dx -
                  renderBox.size.width,
              top: buttonPos.dy - 320,
              child: Material(
                color: Colors.transparent,
                child: _FilterPopupCard(
                  popupWidth: popupWidth,
                  priceFromController: _priceFromController,
                  priceToController: _priceToController,
                  selectedColor: _selectedColor,
                  selectedDelivery: _selectedDelivery,
                  colorOptions: _colorOptions,
                  deliveryOptions: _deliveryOptions,
                  onColorChanged: (v) {
                    _selectedColor = v;
                  },
                  onDeliveryChanged: (v) {
                    _selectedDelivery = v;
                  },
                ),
              ),
            ),
          ],
        );
      },
    );

    Overlay.of(context).insert(_filterOverlay!);
    _filterOpen = true;
    setState(() {});
  }

  Widget _buildToggleOption(String label, bool isSelected) {
    return GestureDetector(
      onTap: () {
        setState(() {
          _isChat = label == 'Chat';
        });
        widget.onModeChanged?.call(_isChat);
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected ? Colors.white : Colors.grey.shade200,
          borderRadius: BorderRadius.circular(18),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.08),
                    blurRadius: 4,
                    offset: const Offset(0, 1),
                  ),
                ]
              : [],
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 13,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
            color: isSelected ? Colors.black87 : Colors.grey.shade500,
          ),
        ),
      ),
    );
  }
}

class _DashedBorderPainter extends CustomPainter {
  final Color color;
  final double strokeWidth;
  final double dashLength;
  final double gapLength;
  final double borderRadius;

  _DashedBorderPainter({
    required this.color,
    required this.strokeWidth,
    required this.dashLength,
    required this.gapLength,
    required this.borderRadius,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = strokeWidth
      ..style = PaintingStyle.stroke;

    final path = Path()
      ..addRRect(
        RRect.fromRectAndRadius(
          Rect.fromLTWH(0, 0, size.width, size.height),
          Radius.circular(borderRadius),
        ),
      );

    final dashPath = _createDashedPath(path);
    canvas.drawPath(dashPath, paint);
  }

  Path _createDashedPath(Path source) {
    final dashedPath = Path();
    for (final metric in source.computeMetrics()) {
      double distance = 0;
      while (distance < metric.length) {
        final end = (distance + dashLength).clamp(0, metric.length).toDouble();
        dashedPath.addPath(metric.extractPath(distance, end), Offset.zero);
        distance += dashLength + gapLength;
      }
    }
    return dashedPath;
  }

  @override
  bool shouldRepaint(covariant _DashedBorderPainter oldDelegate) {
    return oldDelegate.color != color ||
        oldDelegate.strokeWidth != strokeWidth ||
        oldDelegate.dashLength != dashLength ||
        oldDelegate.gapLength != gapLength ||
        oldDelegate.borderRadius != borderRadius;
  }
}

/// Compact filter popup card matching the mockup design
class _FilterPopupCard extends StatefulWidget {
  final double popupWidth;
  final TextEditingController priceFromController;
  final TextEditingController priceToController;
  final String selectedColor;
  final String selectedDelivery;
  final List<String> colorOptions;
  final List<String> deliveryOptions;
  final ValueChanged<String> onColorChanged;
  final ValueChanged<String> onDeliveryChanged;

  const _FilterPopupCard({
    required this.popupWidth,
    required this.priceFromController,
    required this.priceToController,
    required this.selectedColor,
    required this.selectedDelivery,
    required this.colorOptions,
    required this.deliveryOptions,
    required this.onColorChanged,
    required this.onDeliveryChanged,
  });

  @override
  State<_FilterPopupCard> createState() => _FilterPopupCardState();
}

class _FilterPopupCardState extends State<_FilterPopupCard> {
  late String _color;
  late String _delivery;
  bool _colorExpanded = false;
  bool _deliveryExpanded = false;

  @override
  void initState() {
    super.initState();
    _color = widget.colorOptions.contains(widget.selectedColor)
        ? widget.selectedColor
        : widget.colorOptions.first;
    _delivery = widget.deliveryOptions.contains(widget.selectedDelivery)
        ? widget.selectedDelivery
        : widget.deliveryOptions.first;
  }

  InputDecoration _fieldDecoration(String hint) {
    return InputDecoration(
      hintText: hint,
      hintStyle: TextStyle(fontSize: 13, color: Colors.grey.shade500),
      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      isDense: true,
      filled: true,
      fillColor: Colors.grey.shade100,
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: BorderSide.none,
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: BorderSide.none,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: widget.popupWidth,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.10),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Title
          const Text(
            'Filter',
            style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: Colors.black,
            ),
          ),
          const SizedBox(height: 14),

          // PREISSPANNE
          Text(
            'PREISSPANNE',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: Colors.grey.shade600,
              letterSpacing: 0.8,
            ),
          ),
          const SizedBox(height: 6),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: widget.priceFromController,
                  keyboardType: TextInputType.number,
                  style: const TextStyle(fontSize: 13),
                  decoration: _fieldDecoration('Von'),
                ),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 6),
                child: Text(
                  '–',
                  style: TextStyle(fontSize: 14, color: Colors.grey.shade500),
                ),
              ),
              Expanded(
                child: TextField(
                  controller: widget.priceToController,
                  keyboardType: TextInputType.number,
                  style: const TextStyle(fontSize: 13),
                  decoration: _fieldDecoration('Bis'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),

          // FARBEN
          Text(
            'FARBEN',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: Colors.grey.shade600,
              letterSpacing: 0.8,
            ),
          ),
          const SizedBox(height: 6),
          _buildInlineSelector(
            value: _color,
            items: widget.colorOptions,
            expanded: _colorExpanded,
            onTap: () {
              setState(() {
                _colorExpanded = !_colorExpanded;
                _deliveryExpanded = false;
              });
            },
            onChanged: (v) {
              setState(() {
                _color = v;
                _colorExpanded = false;
              });
              widget.onColorChanged(v);
            },
          ),
          const SizedBox(height: 14),

          // DELIVERY TIME
          Text(
            'DELIVERY TIME',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: Colors.grey.shade600,
              letterSpacing: 0.8,
            ),
          ),
          const SizedBox(height: 6),
          _buildInlineSelector(
            value: _delivery,
            items: widget.deliveryOptions,
            expanded: _deliveryExpanded,
            onTap: () {
              setState(() {
                _deliveryExpanded = !_deliveryExpanded;
                _colorExpanded = false;
              });
            },
            onChanged: (v) {
              setState(() {
                _delivery = v;
                _deliveryExpanded = false;
              });
              widget.onDeliveryChanged(v);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildInlineSelector({
    required String value,
    required List<String> items,
    required bool expanded,
    required VoidCallback onTap,
    required ValueChanged<String> onChanged,
  }) {
    // Only show non-selected items in the expanded list
    final otherItems = items.where((i) => i != value).toList();

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // The selector button
        GestureDetector(
          onTap: onTap,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            decoration: BoxDecoration(
              color: Colors.grey.shade100,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    value,
                    style: const TextStyle(fontSize: 13, color: Colors.black87),
                  ),
                ),
                AnimatedRotation(
                  turns: expanded ? 0.5 : 0,
                  duration: const Duration(milliseconds: 200),
                  child: Icon(
                    Icons.keyboard_arrow_down_rounded,
                    size: 20,
                    color: Colors.grey.shade500,
                  ),
                ),
              ],
            ),
          ),
        ),
        // Expanded options list
        AnimatedCrossFade(
          firstChild: const SizedBox.shrink(),
          secondChild: Container(
            margin: const EdgeInsets.only(top: 4),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: Colors.grey.shade200),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.06),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxHeight: 120),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: otherItems.map((item) {
                    return GestureDetector(
                      onTap: () => onChanged(item),
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 10,
                        ),
                        child: Text(
                          item,
                          style: const TextStyle(
                            fontSize: 13,
                            color: Colors.black87,
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),
            ),
          ),
          crossFadeState: expanded
              ? CrossFadeState.showSecond
              : CrossFadeState.showFirst,
          duration: const Duration(milliseconds: 200),
        ),
      ],
    );
  }
}

class _FilePreviewChip extends StatelessWidget {
  final File file;
  final VoidCallback onRemove;

  const _FilePreviewChip({required this.file, required this.onRemove});

  @override
  Widget build(BuildContext context) {
    final String fileName = file.path.split('/').last;
    final String extension = fileName.split('.').last.toLowerCase();
    final bool isImage = ['jpg', 'jpeg', 'png', 'gif'].contains(extension);

    return Container(
      height: 32,
      padding: const EdgeInsets.only(left: 8, right: 4),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.shade300, width: 0.5),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // File icon or thumbnail
          Container(
            width: 20,
            height: 20,
            decoration: BoxDecoration(
              color: _getFileTypeColor(extension),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Center(
              child: isImage
                  ? ClipRRect(
                      borderRadius: BorderRadius.circular(4),
                      child: Image.file(
                        file,
                        width: 20,
                        height: 20,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) =>
                            Icon(Icons.image, size: 12, color: Colors.white),
                      ),
                    )
                  : Icon(
                      _getFileTypeIcon(extension),
                      size: 12,
                      color: Colors.white,
                    ),
            ),
          ),
          const SizedBox(width: 6),
          // File name
          Flexible(
            child: Text(
              fileName.length > 15
                  ? '${fileName.substring(0, 12)}...'
                  : fileName,
              style: const TextStyle(fontSize: 12, color: Colors.black87),
              overflow: TextOverflow.ellipsis,
            ),
          ),
          const SizedBox(width: 4),
          // Remove button
          GestureDetector(
            onTap: onRemove,
            child: Container(
              width: 20,
              height: 20,
              decoration: const BoxDecoration(
                color: Colors.grey,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.close, size: 12, color: Colors.white),
            ),
          ),
        ],
      ),
    );
  }

  Color _getFileTypeColor(String extension) {
    switch (extension) {
      case 'pdf':
        return Colors.red.shade400;
      case 'doc':
      case 'docx':
        return Colors.blue.shade400;
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return Colors.green.shade400;
      case 'txt':
        return Colors.orange.shade400;
      default:
        return Colors.grey.shade400;
    }
  }

  IconData _getFileTypeIcon(String extension) {
    switch (extension) {
      case 'pdf':
        return Icons.picture_as_pdf;
      case 'doc':
      case 'docx':
        return Icons.description;
      case 'txt':
        return Icons.text_snippet;
      default:
        return Icons.insert_drive_file;
    }
  }
}
