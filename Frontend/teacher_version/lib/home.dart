import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:teacher_version/attendance_record_subject_list.dart';
import 'package:teacher_version/toggle_page.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String teacherName = '';
  List<Map<String, String>> subjects = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchTeacherData();
  }

  Future<void> _fetchTeacherData() async {
    final serverUrl = dotenv.env['SERVER_URL'] ?? '';
    final prefs = await SharedPreferences.getInstance();
    final teacherId = prefs.getString('teacher_id');

    if (teacherId == null || serverUrl.isEmpty) {
      Navigator.pushReplacementNamed(context, '/login');
      return;
    }

    try {
      final response = await http.get(
        Uri.parse('$serverUrl/teacher-info?teacher_id=$teacherId'),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final teacherData = data['data']['teacher'];
        final subjectList = List<Map<String, String>>.from(
          data['data']['subjects'].map((subject) => {
            'code': subject['sub_code']?.toString() ?? '',
            'name': subject['sub_name']?.toString() ?? '',
          }),
        );

        setState(() {
          teacherName = teacherData['name'] ?? 'Unknown';
          subjects = subjectList;
          isLoading = false;
        });
      } else {
        _showError('Failed to fetch teacher info');
      }
    } catch (e) {
      _showError('Error fetching teacher data');
    }
  }

  void _showError(String message) {
    setState(() => isLoading = false);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  Future<void> _logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    Navigator.pushReplacementNamed(context, '/login');
  }

  void _goToSubjectUploadPage(String subjectCode, String subjectName) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => SubjectUploadPage(
          subjectCode: subjectCode,
          subjectName: subjectName,
        ),
      ),
    );
  }

  // Navigate to the Attendance Table Page
  void _goToAttendanceRecordPage(String subjectCode) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => SubjectsListPage(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final themeColor = Colors.blueAccent;
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;

    // Calculate font size dynamically based on screen width
    double welcomeTextFontSize = screenWidth * 0.055;
    double subjectsTitleFontSize = screenWidth * 0.055;
    double listItemFontSize = screenWidth * 0.05;

    // Set maximum font size limits
    double maxWelcomeTextFontSize = 24.0;
    double maxSubjectsTitleFontSize = 24.0;
    double maxListItemFontSize = 20.0;

    // Apply the maximum font size limits
    welcomeTextFontSize = welcomeTextFontSize > maxWelcomeTextFontSize ? maxWelcomeTextFontSize : welcomeTextFontSize;
    subjectsTitleFontSize = subjectsTitleFontSize > maxSubjectsTitleFontSize ? maxSubjectsTitleFontSize : subjectsTitleFontSize;
    listItemFontSize = listItemFontSize > maxListItemFontSize ? maxListItemFontSize : listItemFontSize;

    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('Home', style: TextStyle(color: Colors.white)),
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.more_vert, color: Colors.white),
            onSelected: (value) {
              if (value == 'logout') {
                _logout();
              } else if (value == 'attendance_record') {
                // Handle the "Attendance Record" option
                _goToAttendanceRecordPage(subjects.isNotEmpty ? subjects[0]['code'] ?? '' : '');
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(value: 'attendance_record', child: Text('Attendance Record')),
              const PopupMenuItem(value: 'logout', child: Text('Logout')),
            ],
          ),
        ],
      ),
      body: Container(
        width: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF80B3FF), Color(0xFF0000CD)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: SafeArea(
          child: isLoading
              ? const Center(child: CircularProgressIndicator(color: Colors.white))
              : Padding(
            padding: EdgeInsets.symmetric(
              horizontal: screenWidth * 0.06, // 6% of screen width
              vertical: screenHeight * 0.04,  // 4% of screen height
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Welcome, $teacherName',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: welcomeTextFontSize,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 30),
                Center(
                  child: Text(
                    'Subjects You Teach',
                    style: TextStyle(
                      fontSize: subjectsTitleFontSize,
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                Expanded(
                  child: subjects.isEmpty
                      ? const Center(
                    child: Text(
                      'No subjects assigned',
                      style: TextStyle(color: Colors.white, fontSize: 16),
                    ),
                  )
                      : ListView.builder(
                    itemCount: subjects.length,
                    itemBuilder: (context, index) {
                      final subject = subjects[index];
                      return Container(
                        margin: EdgeInsets.symmetric(
                            vertical: screenHeight * 0.01), // 1% of screen height
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(15),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.2),
                              blurRadius: 6,
                              offset: const Offset(0, 3),
                            ),
                          ],
                        ),
                        child: ListTile(
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(15),
                          ),
                          contentPadding: EdgeInsets.symmetric(
                              horizontal: screenWidth * 0.04), // 4% of screen width
                          title: Text(
                            '${subject['name']} (${subject['code']})',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: listItemFontSize,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          trailing: const Icon(Icons.arrow_forward_ios, color: Colors.white),
                          onTap: () => _goToSubjectUploadPage(
                            subject['code']!,
                            subject['name']!,
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
