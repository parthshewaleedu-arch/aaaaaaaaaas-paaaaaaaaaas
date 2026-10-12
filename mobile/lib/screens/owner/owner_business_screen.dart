import 'package:flutter/material.dart';
import '../../core/services/app_repository.dart';
import '../../core/services/storage_service.dart';
import '../../core/theme/app_theme.dart';

class OwnerBusinessScreen extends StatefulWidget {
  const OwnerBusinessScreen({super.key});

  @override
  State<OwnerBusinessScreen> createState() => _OwnerBusinessScreenState();
}

class _OwnerBusinessScreenState extends State<OwnerBusinessScreen> {
  String _ownerEmail = '';
  Map<String, dynamic>? _existingBusiness;

  // Form Fields
  final _nameCtrl = TextEditingController();
  final _addressCtrl = TextEditingController();
  final _googleMapsCtrl = TextEditingController(text: 'https://maps.google.com/?q=18.6757,73.8967');
  final _phoneCtrl = TextEditingController();
  final _whatsappCtrl = TextEditingController();
  final _openingHoursCtrl = TextEditingController(text: '08:30 AM - 10:00 PM');
  final _discountCtrl = TextEditingController();
  final _descCtrl = TextEditingController();

  String _selectedCategory = 'MESS';
  int _monthlyFee = 1500;
  String _priceLevel = '₹';

  @override
  void initState() {
    super.initState();
    // Instant synchronous load - NO SLOW LOADING!
    _loadDataInstantly();
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _addressCtrl.dispose();
    _googleMapsCtrl.dispose();
    _phoneCtrl.dispose();
    _whatsappCtrl.dispose();
    _openingHoursCtrl.dispose();
    _discountCtrl.dispose();
    _descCtrl.dispose();
    super.dispose();
  }

  void _loadDataInstantly() {
    _ownerEmail = StorageService.getCurrentUserEmail();
    _existingBusiness = AppRepository.getBusinessByOwner(_ownerEmail);

    if (_existingBusiness != null) {
      _nameCtrl.text = _existingBusiness!['name'] ?? '';
      _selectedCategory = _existingBusiness!['category_name'] ?? 'MESS';
      _monthlyFee = _existingBusiness!['monthly_fee'] ?? AppRepository.getFeeForCategory(_selectedCategory);
      _addressCtrl.text = _existingBusiness!['address'] ?? '';
      _googleMapsCtrl.text = _existingBusiness!['google_maps_url'] ?? '';
      _phoneCtrl.text = _existingBusiness!['phone'] ?? '';
      _whatsappCtrl.text = _existingBusiness!['whatsapp'] ?? '';
      _openingHoursCtrl.text = _existingBusiness!['opening_hours_text'] ?? '08:30 AM - 10:00 PM';
      _discountCtrl.text = _existingBusiness!['discount_details'] ?? '';
      _descCtrl.text = _existingBusiness!['description'] ?? '';
      _priceLevel = _existingBusiness!['price_level'] ?? '₹';
    } else {
      _selectedCategory = 'MESS';
      _monthlyFee = AppRepository.getFeeForCategory(_selectedCategory);
    }
  }

  void _onCategoryChanged(String newCat) {
    setState(() {
      _selectedCategory = newCat;
      _monthlyFee = AppRepository.getFeeForCategory(newCat);
    });
  }

  Future<void> _handleSaveListing() async {
    final name = _nameCtrl.text.trim();
    final address = _addressCtrl.text.trim();
    final phone = _phoneCtrl.text.trim();

    if (name.isEmpty || address.isEmpty || phone.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter Business Name, Address, and Phone Number')),
      );
      return;
    }

    // Save instantly to AppRepository
    final updated = await AppRepository.addOrUpdateBusiness(
      ownerEmail: _ownerEmail,
      name: name,
      categoryName: _selectedCategory,
      address: address,
      phone: phone,
      whatsapp: _whatsappCtrl.text.trim().isEmpty ? phone : _whatsappCtrl.text.trim(),
      openingHours: _openingHoursCtrl.text.trim(),
      priceLevel: _priceLevel,
      discountDetails: _discountCtrl.text.trim(),
      description: _descCtrl.text.trim(),
      googleMapsUrl: _googleMapsCtrl.text.trim(),
    );

    setState(() {
      _existingBusiness = updated;
    });

    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: AppTheme.success,
        content: Text('✅ "$name" submitted! It is now pending admin approval for the student feed.'),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Text(_existingBusiness == null ? 'List Your Business' : 'Edit Business Listing'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Status Header
            if (_existingBusiness != null)
              Container(
                margin: const EdgeInsets.only(bottom: 16),
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: _existingBusiness!['status'] == 'VERIFIED'
                      ? AppTheme.success.withOpacity(0.12)
                      : AppTheme.secondary.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color: _existingBusiness!['status'] == 'VERIFIED' ? AppTheme.success : AppTheme.secondary,
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      _existingBusiness!['status'] == 'VERIFIED' ? Icons.verified : Icons.hourglass_top,
                      color: _existingBusiness!['status'] == 'VERIFIED' ? AppTheme.success : const Color(0xFFB45309),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        _existingBusiness!['status'] == 'VERIFIED'
                            ? 'Your listing is APPROVED & visible to students.'
                            : 'Status: PENDING REVIEW by Campus Admin.',
                        style: TextStyle(
                          color: _existingBusiness!['status'] == 'VERIFIED' ? AppTheme.success : const Color(0xFFB45309),
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

            // Plan & Fee Callout Banner
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF0F766E), Color(0xFF14B8A6)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Row(
                children: [
                  const Icon(Icons.receipt_long, color: Colors.white, size: 28),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Category: $_selectedCategory',
                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          'Listing Plan: ₹$_monthlyFee / Month',
                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 16),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Business Form
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.border),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Business / Shop Name *', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _nameCtrl,
                    decoration: const InputDecoration(hintText: 'e.g. Sharma Mess, Om Boys Hostel, Laxmi Laundry'),
                  ),
                  const SizedBox(height: 16),

                  // Category Selector with Pricing
                  const Text('Select Business Category *', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14),
                    decoration: BoxDecoration(
                      border: Border.all(color: AppTheme.border),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<String>(
                        value: _selectedCategory,
                        isExpanded: true,
                        items: AppRepository.categoriesWithPlans.map((plan) {
                          return DropdownMenuItem<String>(
                            value: plan.name,
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Flexible(
                                  child: Text(plan.name, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 13)),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: AppTheme.primary.withOpacity(0.08),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text(
                                    '₹${plan.monthlyFee}/mo',
                                    style: const TextStyle(color: AppTheme.primary, fontWeight: FontWeight.bold, fontSize: 11),
                                  ),
                                ),
                              ],
                            ),
                          );
                        }).toList(),
                        onChanged: (val) {
                          if (val != null) _onCategoryChanged(val);
                        },
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Address & Landmark
                  const Text('Address & Campus Landmark *', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _addressCtrl,
                    decoration: const InputDecoration(
                      hintText: 'e.g. Opp. MIT AOE Gate 2, Alandi, Pune (400 m from campus)',
                      prefixIcon: Icon(Icons.location_on_outlined),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Google Maps Location
                  const Text('Google Maps Location / Link *', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _googleMapsCtrl,
                    decoration: const InputDecoration(
                      hintText: 'e.g. https://maps.google.com/?q=18.6757,73.8967 or Latitude, Longitude',
                      prefixIcon: Icon(Icons.map_outlined),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Contact numbers
                  Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('Phone Number *', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                            const SizedBox(height: 6),
                            TextField(
                              controller: _phoneCtrl,
                              keyboardType: TextInputType.phone,
                              decoration: const InputDecoration(hintText: '+91 98765 43210'),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('WhatsApp (Orders)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                            const SizedBox(height: 6),
                            TextField(
                              controller: _whatsappCtrl,
                              keyboardType: TextInputType.phone,
                              decoration: const InputDecoration(hintText: '+91 98765 43210'),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Opening & Closing Hours
                  const Text('Opening & Closing Timings *', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _openingHoursCtrl,
                    decoration: const InputDecoration(
                      hintText: 'e.g. 08:30 AM - 10:30 PM (or 24 Hours for Hostel)',
                      prefixIcon: Icon(Icons.access_time),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Price level
                  const Text('Price Level', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  const SizedBox(height: 6),
                  Row(
                    children: ['₹ (Budget)', '₹₹ (Moderate)', '₹₹₹ (Premium)'].map((lvl) {
                      final code = lvl.split(' ')[0];
                      final isSel = _priceLevel == code;
                      return Padding(
                        padding: const EdgeInsets.only(right: 8.0),
                        child: ChoiceChip(
                          label: Text(lvl, style: const TextStyle(fontSize: 12)),
                          selected: isSel,
                          selectedColor: AppTheme.primary,
                          labelStyle: TextStyle(color: isSel ? Colors.white : AppTheme.textPrimary, fontWeight: FontWeight.bold),
                          onSelected: (val) {
                            if (val) setState(() => _priceLevel = code);
                          },
                        ),
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 16),

                  // Student Discount
                  const Text('Student Discount / Special Offer', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _discountCtrl,
                    decoration: const InputDecoration(
                      hintText: 'e.g. 10% Off with College ID card, or ₹500 off first month deposit',
                      prefixIcon: Icon(Icons.school_outlined),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Description
                  const Text('Business Description / Facilities', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _descCtrl,
                    maxLines: 3,
                    decoration: const InputDecoration(
                      hintText: 'For Hostel: Wi-Fi, Hot water, Study table, CCTV...\nFor Mess: Pure veg, daily sweets, unlimited thali...',
                    ),
                  ),
                  const SizedBox(height: 24),

                  ElevatedButton.icon(
                    icon: const Icon(Icons.publish_rounded),
                    label: Text(_existingBusiness == null ? 'Submit & List Business' : 'Save & Update Listing'),
                    onPressed: _handleSaveListing,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
