import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';

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
  String searchQuery = '';
  bool isLoading = false;

  String get date => DateTime.now()
      .toString()
      .substring(0, 10)
      .split('-')
      .reversed
      .join('-');

  Future<void> fetchAttendance() async {
    final serverUrl = dotenv.env['SERVER_URL'] ?? '';
    setState(() => isLoading = true);

    try {
      final response = await http.get(
        Uri.parse('$serverUrl/get_attendance?subjectCode=${widget.subjectCode}&date=$date'),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success']) {
          setState(() {
            presentStudents = List<String>.from(data['data'] ?? []);
            allStudents = List<String>.from(data['all'] ?? []);
            taggedImages = List<String>.from(data['tagged_images'] ?? []);
          });
        } else {
          print("Error: ${data['message']}");
        }
      } else {
        print("Server error: ${response.statusCode}");
      }
    } catch (e) {
      print("Fetch error: $e");
    } finally {
      setState(() => isLoading = false);
    }
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
  Widget build(BuildContext context) {
    final imageBaseUrl = dotenv.env['SERVER_URL'] ?? '';
    final screenWidth = MediaQuery.of(context).size.width;

    return Scaffold(
      backgroundColor: Colors.blue.shade50,
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Search Roll Number',
                prefixIcon: const Icon(Icons.search),
                border: const OutlineInputBorder(),
              ),
              onChanged: (value) => setState(() => searchQuery = value),
            ),
          ),
          Expanded(
            child: isLoading
                ? const Center(child: CircularProgressIndicator())
                : CustomScrollView(
              slivers: [
                _buildStudentSliverSection('Present Students', filteredPresentStudents, Colors.green),
                _buildStudentSliverSection('Absent Students', filteredAbsentStudents, Colors.red),
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
                        final imgName = taggedImages[index];
                        final imgUrl = '$imageBaseUrl/Attendance_Records/$imgName';
                        print('Loading image: $imgUrl');

                        return Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(12),
                            child: InteractiveViewer(
                              panEnabled: true,
                              minScale: 0.8,
                              maxScale: 3.0,
                              child: Image.network(
                                imgUrl,
                                fit: BoxFit.cover,
                                loadingBuilder: (context, child, loadingProgress) {
                                  if (loadingProgress == null) return child;
                                  return Center(
                                    child: CircularProgressIndicator(
                                      value: loadingProgress.expectedTotalBytes != null
                                          ? loadingProgress.cumulativeBytesLoaded /
                                          loadingProgress.expectedTotalBytes!
                                          : null,
                                    ),
                                  );
                                },
                                errorBuilder: (context, error, stackTrace) {
                                  print('Image loading error: $error');
                                  return Container(
                                    color: Colors.grey[200],
                                    child: const Center(
                                      child: Icon(Icons.error, color: Colors.red),
                                    ),
                                  );
                                },
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
