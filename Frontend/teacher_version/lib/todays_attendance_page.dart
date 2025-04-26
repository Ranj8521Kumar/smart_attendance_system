import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:collection/collection.dart';

class TodaysAttendancePage extends StatefulWidget {
  final String subjectCode;
  final String subjectName;

  const TodaysAttendancePage({
    Key? key,
    required this.subjectCode,
    required this.subjectName,
  }) : super(key: key);

  @override
  _TodaysAttendancePageState createState() => _TodaysAttendancePageState();
}

class _TodaysAttendancePageState extends State<TodaysAttendancePage> {
  List<String> presentStudents = [];
  List<String> allStudents = [];
  List<String> taggedImages = [];
  List<String> previousTaggedImages = [];
  String searchQuery = '';
  bool isLoading = false;
  String? errorMessage;
  Timer? _debounce;

  bool hasFetchedData = false;

  String get formattedDate => DateTime.now()
      .toString()
      .substring(0, 10)
      .split('-')
      .reversed
      .join('-');

  Future<void> fetchAttendance() async {
    final serverUrl = dotenv.env['SERVER_URL'] ?? '';
    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    try {
      final response = await http.get(
        Uri.parse('$serverUrl/get_attendance?subjectCode=${widget.subjectCode}&date=$formattedDate'),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode != 200) {
        throw Exception('Server error: ${response.statusCode}');
      }

      final data = json.decode(response.body);
      if (data['success'] != true) {
        throw Exception(data['message'] ?? 'Failed to fetch attendance');
      }

      List<String> newTaggedImages = List<String>.from(data['tagged_images'] ?? []);

      if (!ListEquality().equals(newTaggedImages, previousTaggedImages)) {
        setState(() {
          presentStudents = List<String>.from(data['data'] ?? []);
          allStudents = List<String>.from(data['all'] ?? []);
          taggedImages = newTaggedImages;
          previousTaggedImages = newTaggedImages;
        });
      }

      hasFetchedData = true;
    } on TimeoutException {
      setState(() => errorMessage = 'Request timed out. Please try again.');
    } catch (e) {
      // Handle different types of exceptions more gracefully
      String errorStr = e.toString();
      if (e is Exception) {
        // If it's an exception, get the error message without the "Exception:" prefix
        errorStr = errorStr.replaceAll('Exception:', '').trim();
      }
      setState(() => errorMessage = errorStr);
    } finally {
      setState(() => isLoading = false);
    }
  }


  Future<void> _onRefresh() async {
    setState(() => hasFetchedData = false);
    await fetchAttendance();
  }

  void onSearchChanged(String query) {
    if (_debounce?.isActive ?? false) _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 500), () {
      setState(() => searchQuery = query);
    });
  }

  List<String> get filteredPresentStudents => presentStudents
      .where((roll) => roll.toLowerCase().contains(searchQuery.toLowerCase()))
      .toList();

  List<String> get absentStudents =>
      allStudents.where((roll) => !presentStudents.contains(roll)).toList();

  List<String> get filteredAbsentStudents => absentStudents
      .where((roll) => roll.toLowerCase().contains(searchQuery.toLowerCase()))
      .toList();

  @override
  void initState() {
    super.initState();
    fetchAttendance();
  }

  @override
  void dispose() {
    _debounce?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final imageBaseUrl = dotenv.env['SERVER_URL'] ?? '';

    return Scaffold(
      backgroundColor: Colors.blue.shade50,
      body: RefreshIndicator(
        onRefresh: _onRefresh,
        child: isLoading
            ? const Center(child: CircularProgressIndicator())
            : errorMessage != null
            ? Center(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              errorMessage!,
              style: const TextStyle(
                fontSize: 20,
                color: Colors.black,  // Set text color to black
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
          ),
        )
            : Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: TextField(
                decoration: const InputDecoration(
                  hintText: 'Search Roll Number',
                  prefixIcon: Icon(Icons.search),
                  border: OutlineInputBorder(),
                ),
                onChanged: onSearchChanged,
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: _buildSummaryCards(),
            ),
            const SizedBox(height: 8),
            Expanded(
              child: CustomScrollView(
                slivers: [
                  _buildStudentSliverSection(
                    'Present Students',
                    filteredPresentStudents,
                    Colors.green,
                  ),
                  _buildStudentSliverSection(
                    'Absent Students',
                    filteredAbsentStudents,
                    Colors.red,
                  ),
                  if (taggedImages.isNotEmpty)
                    _buildTaggedImagesSection(imageBaseUrl),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryCards() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        _buildSummaryCard('Total', allStudents.length, Colors.blue),
        _buildSummaryCard('Present', presentStudents.length, Colors.green),
        _buildSummaryCard('Absent', absentStudents.length, Colors.red),
      ],
    );
  }

  Widget _buildSummaryCard(String title, int count, Color color) {
    return Expanded(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 4),
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: color.withOpacity(0.4)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              title,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              count.toString(),
              style: const TextStyle(
                fontSize: 17,
                fontWeight: FontWeight.bold,
                color: Colors.black,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStudentSliverSection(String title, List<String> students, Color color) {
    return SliverPadding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      sliver: SliverToBoxAdapter(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withOpacity(0.05),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: color.withOpacity(0.3)),
              ),
              child: students.isEmpty
                  ? Center(
                child: Text(
                  'No $title found',
                  style: TextStyle(
                    color: color.withOpacity(0.6),
                    fontSize: 16,
                  ),
                ),
              )
                  : Text(
                students.join(', '),
                style: const TextStyle(
                  color: Colors.black,
                  fontSize: 18,
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildTaggedImagesSection(String baseUrl) {
    return SliverList(
      delegate: SliverChildListDelegate(
        [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              'Tagged Images',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.indigo[700],
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 1,
                mainAxisSpacing: 16,
                childAspectRatio: 0.8,
              ),
              itemCount: taggedImages.length,
              itemBuilder: (context, index) {
                final imgName = taggedImages[index];
                final imgUrl = '$baseUrl/Attendance_Records/$imgName';

                return ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: GestureDetector(
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => FullScreenImagePage(imageUrl: imgUrl),
                        ),
                      );
                    },
                    child: InteractiveViewer(
                      panEnabled: true,
                      minScale: 0.8,
                      maxScale: 3.0,
                      child: CachedNetworkImage(
                        imageUrl: imgUrl,
                        fit: BoxFit.cover,
                        placeholder: (context, url) => const Center(
                          child: CircularProgressIndicator(),
                        ),
                        errorWidget: (context, url, error) => Container(
                          color: Colors.grey[200],
                          child: const Center(
                            child: Icon(Icons.error, color: Colors.red),
                          ),
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class FullScreenImagePage extends StatelessWidget {
  final String imageUrl;

  const FullScreenImagePage({Key? key, required this.imageUrl}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Center(
        child: InteractiveViewer(
          panEnabled: true,
          minScale: 0.8,
          maxScale: 100.0,
          child: CachedNetworkImage(
            imageUrl: imageUrl,
            fit: BoxFit.contain,
            placeholder: (context, url) => const Center(
              child: CircularProgressIndicator(),
            ),
            errorWidget: (context, url, error) => const Icon(Icons.error, color: Colors.red),
          ),
        ),
      ),
    );
  }
}
