import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

class OwnerServicesScreen extends StatefulWidget {
  const OwnerServicesScreen({super.key});

  @override
  State<OwnerServicesScreen> createState() => _OwnerServicesScreenState();
}

class _OwnerServicesScreenState extends State<OwnerServicesScreen> {
  final List<Map<String, dynamic>> _services = [
    {
      'id': 'srv-1',
      'name': 'Unlimited Student Thali',
      'price': 90.0,
      'description': '2 sabzi, 4 chapati/roti, dal tadka, rice, salad & sweet on Sun',
      'last_updated': 'Today',
    },
    {
      'id': 'srv-2',
      'name': 'Single Meal Tiffin Box',
      'price': 75.0,
      'description': 'Packed hot in disposable foil containers with pickle',
      'last_updated': 'Yesterday',
    },
    {
      'id': 'srv-3',
      'name': 'Monthly Mess Pass (Lunch + Dinner)',
      'price': 2400.0,
      'description': '60 meals booklet valid for 35 days, includes Sunday special',
      'last_updated': '3 days ago',
    },
    {
      'id': 'srv-4',
      'name': 'Extra Chapati / Roti (Pack of 2)',
      'price': 15.0,
      'description': 'Hot wheat rotis with ghee option',
      'last_updated': '1 week ago',
    },
  ];

  void _showAddServiceDialog() {
    final nameCtrl = TextEditingController();
    final priceCtrl = TextEditingController();
    final descCtrl = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Add Menu Item / Service'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameCtrl,
              decoration: const InputDecoration(labelText: 'Item / Service Name', hintText: 'e.g. Special Paneer Thali'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: priceCtrl,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Price (₹)', hintText: 'e.g. 110'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: descCtrl,
              decoration: const InputDecoration(labelText: 'Description / Details', hintText: 'Portion size, inclusions...'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              if (nameCtrl.text.isNotEmpty && priceCtrl.text.isNotEmpty) {
                setState(() {
                  _services.insert(0, {
                    'id': 'srv-${DateTime.now().millisecondsSinceEpoch}',
                    'name': nameCtrl.text.trim(),
                    'price': double.tryParse(priceCtrl.text) ?? 50.0,
                    'description': descCtrl.text.trim(),
                    'last_updated': 'Just now',
                  });
                });
                Navigator.pop(ctx);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Item added and published to campus menu!')),
                );
              }
            },
            child: const Text('Add Item'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Menu & Services Pricing'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add, color: AppTheme.primary),
            onPressed: _showAddServiceDialog,
          ),
        ],
      ),
      body: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: _services.length,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (ctx, idx) {
          final s = _services[idx];
          return Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppTheme.border),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        s['name'] as String,
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        s['description'] as String,
                        style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary),
                      ),
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: AppTheme.success.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          'Price Freshness: ${s['last_updated']}',
                          style: const TextStyle(color: AppTheme.success, fontSize: 10, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      '₹${(s['price'] as double).round()}',
                      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: AppTheme.primary),
                    ),
                    IconButton(
                      icon: const Icon(Icons.delete_outline, size: 20, color: AppTheme.textMuted),
                      onPressed: () {
                        setState(() => _services.removeAt(idx));
                      },
                    ),
                  ],
                ),
              ],
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppTheme.primary,
        icon: const Icon(Icons.add, color: Colors.white),
        label: const Text('Add Dish / Service', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        onPressed: _showAddServiceDialog,
      ),
    );
  }
}
