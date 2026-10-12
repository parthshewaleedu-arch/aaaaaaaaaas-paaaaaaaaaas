import 'package:flutter/material.dart';
import '../../core/services/api_service.dart';
import '../../core/theme/app_theme.dart';
import '../../models/business_model.dart';

class OwnerBusinessScreen extends StatefulWidget {
  const OwnerBusinessScreen({super.key});

  @override
  State<OwnerBusinessScreen> createState() => _OwnerBusinessScreenState();
}

class _OwnerBusinessScreenState extends State<OwnerBusinessScreen> {
  bool _isLoading = false;
  bool _isCreatingNew = false;
  BusinessModel? _myBusiness;

  // Form controllers
  final _nameController = TextEditingController(text: 'Sharma Mess & Tiffin Service');
  final _categoryController = TextEditingController(text: 'Food & Mess');
  final _addressController = TextEditingController(text: 'Near MIT AOE Back Gate, Alandi, Pune');
  final _phoneController = TextEditingController(text: '+91 98234 56789');
  final _whatsappController = TextEditingController(text: '+91 98234 56789');
  final _descController = TextEditingController(text: 'Fresh and hygienic student mess serving pure vegetarian unlimited thali and monthly tiffin subscriptions.');
  final _discountController = TextEditingController(text: '15% Off Monthly Mess Pass with MIT AOE ID');
  final _hoursController = TextEditingController(text: '08:00 AM - 10:30 PM');
  String _priceLevel = '₹';

  String _verificationStatus = 'VERIFIED'; // UNVERIFIED, PENDING_REVIEW, VERIFIED

  @override
  void initState() {
    super.initState();
    _loadBusiness();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _categoryController.dispose();
    _addressController.dispose();
    _phoneController.dispose();
    _whatsappController.dispose();
    _descController.dispose();
    _discountController.dispose();
    _hoursController.dispose();
    super.dispose();
  }

  Future<void> _loadBusiness() async {
    setState(() => _isLoading = true);
    final res = await ApiService.getMyBusiness();
    if (res.success && res.data != null) {
      _myBusiness = BusinessModel.fromJson(res.data!);
      _nameController.text = _myBusiness!.name;
      _addressController.text = _myBusiness!.address;
      _categoryController.text = _myBusiness!.categoryName;
      _descController.text = _myBusiness!.description ?? _descController.text;
      _priceLevel = _myBusiness!.priceLevel;
    } else {
      // Load sample for existing business
      _myBusiness = BusinessModel(
        id: 'owner-biz-1',
        name: 'Sharma Mess & Tiffin Service',
        categoryName: 'Food & Mess',
        address: 'Near MIT AOE Back Gate, Alandi, Pune',
        rating: 4.6,
        reviewCount: 42,
        isVerified: true,
        priceLevel: '₹',
        hasStudentDiscount: true,
        discountDetails: '15% Off Monthly Mess Pass with MIT AOE ID',
        description: 'Fresh and hygienic student mess serving pure vegetarian unlimited thali and monthly tiffin subscriptions.',
      );
    }
    if (mounted) setState(() => _isLoading = false);
  }

  Future<void> _saveBusiness() async {
    if (_nameController.text.trim().isEmpty || _addressController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill in business name and address')),
      );
      return;
    }

    setState(() => _isLoading = true);

    final payload = {
      'name': _nameController.text.trim(),
      'category_name': _categoryController.text.trim(),
      'address': _addressController.text.trim(),
      'phone': _phoneController.text.trim(),
      'whatsapp': _whatsappController.text.trim(),
      'description': _descController.text.trim(),
      'price_level': _priceLevel,
      'student_discount': _discountController.text.trim().isNotEmpty,
      'discount_details': _discountController.text.trim(),
      'opening_hours_text': _hoursController.text.trim(),
    };

    final res = await ApiService.createBusiness(payload);

    if (!mounted) return;
    setState(() {
      _isLoading = false;
      _isCreatingNew = false;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Shop listing published successfully to AAS PAAS!')),
    );
    _loadBusiness();
  }

  void _submitVerification() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Submit for Campus Verification'),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Verified businesses earn higher student trust and a permanent 🟢 Verified badge.',
              style: TextStyle(fontSize: 13, color: AppTheme.textSecondary),
            ),
            SizedBox(height: 12),
            Text('Requirements:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
            SizedBox(height: 4),
            Text('• Shop registration or electricity bill proof\n• Valid contact number & UPI payment ID\n• Physical store presence within 3 km of campus', style: TextStyle(fontSize: 12, height: 1.4)),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);
              setState(() => _verificationStatus = 'PENDING_REVIEW');
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Verification documents submitted. Admin team will review within 24 hours.')),
              );
            },
            child: const Text('Submit Request'),
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
        title: Text(_isCreatingNew ? 'List New Business' : 'My Business Listing'),
        actions: [
          if (!_isCreatingNew)
            IconButton(
              icon: const Icon(Icons.add_business_rounded, color: AppTheme.primary),
              tooltip: 'List Another Shop',
              onPressed: () => setState(() => _isCreatingNew = true),
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Verification Status Card
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppTheme.border),
                    ),
                    child: Row(
                      children: [
                        CircleAvatar(
                          radius: 20,
                          backgroundColor: _verificationStatus == 'VERIFIED'
                              ? AppTheme.success.withOpacity(0.12)
                              : AppTheme.secondary.withOpacity(0.15),
                          child: Icon(
                            _verificationStatus == 'VERIFIED' ? Icons.verified : Icons.pending,
                            color: _verificationStatus == 'VERIFIED' ? AppTheme.success : AppTheme.secondary,
                            size: 22,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                _verificationStatus == 'VERIFIED' ? 'Verified Campus Partner' : 'Verification Status',
                                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                _verificationStatus == 'VERIFIED'
                                    ? 'Your listing displays the verified student trust badge.'
                                    : 'Submit your business proof to get verified.',
                                style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary),
                              ),
                            ],
                          ),
                        ),
                        if (_verificationStatus != 'VERIFIED')
                          TextButton(
                            onPressed: _submitVerification,
                            child: const Text('Verify Now'),
                          ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 20),

                  // Business Listing Form
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
                        const Text('Business Name', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                        const SizedBox(height: 6),
                        TextField(
                          controller: _nameController,
                          decoration: const InputDecoration(hintText: 'e.g. Sharma Mess, Om Xerox Hub'),
                        ),
                        const SizedBox(height: 16),

                        const Text('Category', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                        const SizedBox(height: 6),
                        TextField(
                          controller: _categoryController,
                          decoration: const InputDecoration(hintText: 'e.g. Food & Mess, Cafe, Laundry, Xerox'),
                        ),
                        const SizedBox(height: 16),

                        const Text('Campus Proximity / Address', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                        const SizedBox(height: 6),
                        TextField(
                          controller: _addressController,
                          decoration: const InputDecoration(hintText: 'e.g. Opp. MIT AOE Gate 2, Alandi, Pune'),
                        ),
                        const SizedBox(height: 16),

                        Row(
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text('Contact Phone', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                                  const SizedBox(height: 6),
                                  TextField(
                                    controller: _phoneController,
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
                                  const Text('WhatsApp (Orders)', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                                  const SizedBox(height: 6),
                                  TextField(
                                    controller: _whatsappController,
                                    keyboardType: TextInputType.phone,
                                    decoration: const InputDecoration(hintText: '+91 98765 43210'),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),

                        const Text('Opening & Closing Hours', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                        const SizedBox(height: 6),
                        TextField(
                          controller: _hoursController,
                          decoration: const InputDecoration(hintText: 'e.g. 08:30 AM - 10:30 PM'),
                        ),
                        const SizedBox(height: 16),

                        const Text('Price Level', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                        const SizedBox(height: 6),
                        Row(
                          children: ['₹', '₹₹', '₹₹₹'].map((lvl) {
                            final isSel = _priceLevel == lvl;
                            return Padding(
                              padding: const EdgeInsets.only(right: 8.0),
                              child: ChoiceChip(
                                label: Text(lvl),
                                selected: isSel,
                                selectedColor: AppTheme.primary,
                                labelStyle: TextStyle(
                                  color: isSel ? Colors.white : AppTheme.textPrimary,
                                  fontWeight: FontWeight.bold,
                                ),
                                onSelected: (val) {
                                  if (val) setState(() => _priceLevel = lvl);
                                },
                              ),
                            );
                          }).toList(),
                        ),
                        const SizedBox(height: 16),

                        const Text('Student Discount Offer', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                        const SizedBox(height: 6),
                        TextField(
                          controller: _discountController,
                          decoration: const InputDecoration(
                            hintText: 'e.g. 10% Off on all student meals with College ID',
                            prefixIcon: Icon(Icons.school, color: AppTheme.primary, size: 20),
                          ),
                        ),
                        const SizedBox(height: 16),

                        const Text('About Your Business / Speciality', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                        const SizedBox(height: 6),
                        TextField(
                          controller: _descController,
                          maxLines: 3,
                          decoration: const InputDecoration(
                            hintText: 'Describe meal options, print speeds, laundry turnaround, hygiene...',
                          ),
                        ),
                        const SizedBox(height: 24),

                        ElevatedButton(
                          onPressed: _saveBusiness,
                          child: Text(_isCreatingNew ? 'Publish New Listing' : 'Save Changes'),
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
