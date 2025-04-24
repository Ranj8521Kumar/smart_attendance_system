import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:collection/collection.dart'; // For ListEquality

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
  List<String> previousTaggedImages = [];  // Track previously loaded images
  String searchQuery = '';
  bool isLoading = false;
  String? errorMessage;

  bool hasFetchedData = false; // Flag to prevent multiple fetch calls

  Timer? _debounce;

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
      if (!data['success']) {
        throw Exception(data['message'] ?? 'Failed to fetch attendance');
      }

      // Only update the images if there are new images from the server
      List<String> newTaggedImages = List<String>.from(data['tagged_images'] ?? []);
      if (!ListEquality().equals(newTaggedImages, previousTaggedImages)) {
        setState(() {
          presentStudents = List<String>.from(data['data'] ?? []);
          allStudents = List<String>.from(data['all'] ?? []);
          taggedImages = newTaggedImages; // Update with new images
        });

        // Update the previous image list
        previousTaggedImages = newTaggedImages;
      }

      hasFetchedData = true; // Mark as fetched
    } on http.ClientException catch (e) {
      setState(() => errorMessage = 'Network error: ${e.message}');
    } on TimeoutException {
      setState(() => errorMessage = 'Request timed out');
    } catch (e) {
      setState(() => errorMessage = e.toString());
    } finally {
      setState(() => isLoading = false);
    }
  }

  // Pull-to-refresh handler
  Future<void> _onRefresh() async {
    setState(() {
      hasFetchedData = false;  // Reset fetched data flag to refetch
    });
    await fetchAttendance();
  }

  void onSearchChanged(String query) {
    if (_debounce?.isActive ?? false) _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 500), () {
      setState(() {
        searchQuery = query;
      });
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
    fetchAttendance(); // Fetch attendance when the page is first loaded
  }

  @override
  Widget build(BuildContext context) {
    final imageBaseUrl = dotenv.env['SERVER_URL'] ?? '';

    return Scaffold(
      backgroundColor: Colors.blue.shade50,
      body: RefreshIndicator(
        onRefresh: _onRefresh,  // Pull-to-refresh functionality
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: TextField(
                decoration: const InputDecoration(
                  hintText: 'Search Roll Number',
                  prefixIcon: Icon(Icons.search),
                  border: OutlineInputBorder(),
                ),
                onChanged: onSearchChanged, // Debounced search
              ),
            ),
            if (errorMessage != null)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  errorMessage!,
                  style: const TextStyle(color: Colors.red, fontSize: 16),
                ),
              ),
            Expanded(
              child: isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : CustomScrollView(
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
                    SliverPadding(
                      padding: const EdgeInsets.all(16),
                      sliver: SliverToBoxAdapter(
                        child: Text(
                          'Tagged Images',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: Colors.indigo[700],
                          ),
                        ),
                      ),
                    ),
                  if (taggedImages.isNotEmpty)
                    SliverGrid(
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 1,
                        mainAxisSpacing: 16,
                        childAspectRatio: 0.8,
                      ),
                      delegate: SliverChildBuilderDelegate(
                            (context, index) {
                          final imageName = taggedImages[index];
                          final imgUrl = '$imageBaseUrl/Attendance_Records/$imageName';
                          print('🖼️ Loading image: $imgUrl'); // Debug print

                          return Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 16),
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(12),
                              child: GestureDetector(
                                onTap: () {
                                  // Navigate to Full-Screen Image Page
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
                            ),
                          );
                        },
                        childCount: taggedImages.length,
                      ),
                    ),
                ],
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
          panEnabled: true, // Allow panning
          minScale: 0.8,    // Minimum zoom scale
          maxScale: 100.0,    // Maximum zoom scale
          child: CachedNetworkImage(
            imageUrl: imageUrl,
            fit: BoxFit.contain,
            placeholder: (context, url) => const Center(
              child: CircularProgressIndicator(),
            ),
            errorWidget: (context, url, error) => const Center(
              child: Icon(Icons.error, color: Colors.red),
            ),
          ),
        ),
      ),
    );
  }
}
