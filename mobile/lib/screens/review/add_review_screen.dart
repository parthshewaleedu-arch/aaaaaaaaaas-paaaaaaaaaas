import 'package:flutter/material.dart';
import '../../core/services/api_service.dart';
import '../../core/theme/app_theme.dart';

class AddReviewScreen extends StatefulWidget {
  final String businessId;
  final String businessName;

  const AddReviewScreen({
    super.key,
    required this.businessId,
    required this.businessName,
  });

  @override
  State<AddReviewScreen> createState() => _AddReviewScreenState();
}

class _AddReviewScreenState extends State<AddReviewScreen> {
  final _commentController = TextEditingController();
  double _overallRating = 5.0;
  double _qualityRating = 4.5;
  double _hygieneRating = 4.0;
  double _valueRating = 4.5;
  double _serviceRating = 4.0;
  bool _isSubmitting = false;

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  Future<void> _handleSubmit() async {
    if (_commentController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please write a short review sharing your experience')),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    final res = await ApiService.submitReview(
      businessId: widget.businessId,
      rating: _overallRating,
      comment: _commentController.text.trim(),
      dimensionRatings: {
        'Quality': _qualityRating,
        'Hygiene': _hygieneRating,
        'Value': _valueRating,
        'Service': _serviceRating,
      },
    );

    if (!mounted) return;
    setState(() => _isSubmitting = false);

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Thank you! Your verified student review was submitted.')),
    );
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Write Student Review'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              widget.businessName,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            const Text(
              'Your review helps fellow campus students make better choices.',
              style: TextStyle(fontSize: 13, color: AppTheme.textSecondary),
            ),
            const SizedBox(height: 24),

            // Overall Star Rating
            const Center(
              child: Text(
                'Overall Rating',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(5, (index) {
                final starValue = index + 1;
                return IconButton(
                  iconSize: 36,
                  icon: Icon(
                    starValue <= _overallRating ? Icons.star_rounded : Icons.star_border_rounded,
                    color: AppTheme.secondary,
                  ),
                  onPressed: () => setState(() => _overallRating = starValue.toDouble()),
                );
              }),
            ),
            const SizedBox(height: 24),

            // Dimension Sliders
            const Text(
              'Detailed Category Ratings',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
            ),
            const SizedBox(height: 12),

            _buildSliderRow('Quality of Work / Food', _qualityRating, (v) => setState(() => _qualityRating = v)),
            _buildSliderRow('Hygiene & Cleanliness', _hygieneRating, (v) => setState(() => _hygieneRating = v)),
            _buildSliderRow('Value for Money', _valueRating, (v) => setState(() => _valueRating = v)),
            _buildSliderRow('Staff / Service Speed', _serviceRating, (v) => setState(() => _serviceRating = v)),

            const SizedBox(height: 24),

            // Comment textfield
            const Text(
              'Write Your Review',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _commentController,
              maxLines: 4,
              decoration: const InputDecoration(
                hintText: 'Share details about taste, portion size, price honesty, or student discount availability...',
              ),
            ),
            const SizedBox(height: 32),

            ElevatedButton(
              onPressed: _isSubmitting ? null : _handleSubmit,
              child: _isSubmitting
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                    )
                  : const Text('Submit Review'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSliderRow(String title, double value, ValueChanged<double> onChanged) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        children: [
          Expanded(
            flex: 4,
            child: Text(title, style: const TextStyle(fontSize: 13, color: AppTheme.textSecondary)),
          ),
          Expanded(
            flex: 5,
            child: Slider(
              value: value,
              min: 1.0,
              max: 5.0,
              divisions: 8,
              activeColor: AppTheme.primary,
              label: value.toStringAsFixed(1),
              onChanged: onChanged,
            ),
          ),
          SizedBox(
            width: 28,
            child: Text(value.toStringAsFixed(1), style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
          ),
        ],
      ),
    );
  }
}
