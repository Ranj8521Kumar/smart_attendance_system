import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'attendance_record_table.dart';
import 'package:flutter/services.dart'; // Import the services package for orientation control

class SubjectsListPage extends StatefulWidget {
  const SubjectsListPage({Key? key}) : super(key: key);

  @override
  _SubjectsListPageState createState() => _SubjectsListPageState();
}

class _SubjectsListPageState extends State<SubjectsListPage> {
  List<Map<String, String>> subjects = [];
  bool isLoading = true; // Set initial loading state to true
  String? errorMessage;

  @override
  void initState() {
    super.initState();
    _fetchSubjects();
  }

  Future<void> _fetchSubjects() async {
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
        final subjectList = List<Map<String, String>>.from(
          data['data']['subjects'].map((subject) => {
            'code': subject['sub_code']?.toString() ?? '',
            'name': subject['sub_name']?.toString() ?? '',
          }),
        );

        setState(() {
          subjects = subjectList;
          isLoading = false;
        });
      } else {
        setState(() {
          errorMessage = 'Failed to fetch teacher info';
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        errorMessage = 'Error fetching teacher data';
        isLoading = false;
      });
    }
  }

  Widget _buildSubjectCard(Map<String, String> subject) {
    final width = MediaQuery.of(context).size.width;

    double padding = width * 0.05;

    // Calculate font size based on screen width and set maximum size
    double titleFontSize = width * 0.05;
    double subtitleFontSize = width * 0.045;

    // Set maximum font size limits
    double maxTitleFontSize = 20.0;
    double maxSubtitleFontSize = 15.0;

    titleFontSize = titleFontSize > maxTitleFontSize ? maxTitleFontSize : titleFontSize;
    subtitleFontSize = subtitleFontSize > maxSubtitleFontSize ? maxSubtitleFontSize : subtitleFontSize;

    return Card(
      elevation: 8,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      margin: EdgeInsets.symmetric(vertical: 8),
      color: Colors.blue.shade800,
      child: Container(
        decoration: BoxDecoration(
          color: Colors.blue.shade800,
          borderRadius: BorderRadius.circular(16),
        ),
        child: ListTile(
          contentPadding: EdgeInsets.symmetric(
            horizontal: padding,
            vertical: padding / 2,
          ),
          title: Text(
            subject['name'] ?? 'Unknown Subject',
            style: TextStyle(
              fontSize: titleFontSize,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          subtitle: Text(
            subject['code'] ?? '',
            style: TextStyle(
              fontSize: subtitleFontSize,
              color: Colors.white70,
            ),
          ),
          trailing: const Icon(Icons.arrow_forward_ios, color: Colors.white),
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => AttendanceTablePage(
                  subjectCode: subject['code'] ?? '',
                  subjectName: subject['name'] ?? '',
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    final height = MediaQuery.of(context).size.height;

    double titleFontSize = width * 0.065;
    double errorMessageFontSize = width * 0.05;

    // Set maximum font size limits for title and error message
    double maxTitleFontSize = 20.0;
    double maxErrorMessageFontSize = 10.0;

    titleFontSize = titleFontSize > maxTitleFontSize ? maxTitleFontSize : titleFontSize;
    errorMessageFontSize = errorMessageFontSize > maxErrorMessageFontSize ? maxErrorMessageFontSize : errorMessageFontSize;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Subjects List'),
        backgroundColor: Colors.blueAccent.shade200,
        elevation: 0,
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF80B3FF), Color(0xFF0000CD)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: isLoading
            ? const Center(child: CircularProgressIndicator(color: Colors.white))
            : errorMessage != null
            ? Center(
          child: Padding(
            padding: EdgeInsets.all(width * 0.04),
            child: Text(
              errorMessage!,
              style: TextStyle(
                fontSize: errorMessageFontSize,
                color: Colors.red,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
          ),
        )
            : Padding(
          padding: EdgeInsets.all(width * 0.04),
          child: ListView(
            children: [
              SizedBox(height: height * 0.02),
              ...subjects.map(_buildSubjectCard).toList(),
            ],
          ),
        ),
      ),
    );
  }
}
