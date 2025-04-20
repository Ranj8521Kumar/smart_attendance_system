import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:teacher_version/upload_image.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String teacherName = '';
  List<String> subjects = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchTeacherData();
  }

  Future<void> _fetchTeacherData() async {
    final prefs = await SharedPreferences.getInstance();

    final teacherId = prefs.getString('teacher_id');
    print('Fetched teacher ID: $teacherId');

    if (teacherId == null) {
      Navigator.pushReplacementNamed(context, '/login');
      return;
    }

    try {
      final response = await http.get(
        Uri.parse('http://192.168.25.109:5000/teacher-info?teacher_id=$teacherId'),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final responseData = data['data'];

        final teacherData = responseData['teacher'];
        final subjectCodes = List<String>.from(responseData['subjects']);

        // Debug prints
        print('Teacher: ${teacherData['name']}');
        print('Subjects: $subjectCodes');

        setState(() {
          teacherName = teacherData['name'] ?? 'Unknown';
          subjects = subjectCodes; // Now it's already a List<String>
          isLoading = false;
        });
      } else {
        throw Exception('Failed to fetch teacher info');
      }
    } catch (e) {
      print('Error fetching teacher data: $e');
      setState(() {
        isLoading = false;
      });
    }
  }


  Future<void> _logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear(); // Clear session info
    Navigator.pushReplacementNamed(context, '/login');
  }

  void _goToSubjectUploadPage(String subject) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => SubjectUploadPage(subject: subject),
      ),
    );
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      body: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 50),
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF4B0082), Color(0xFF0000CD)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: isLoading
            ? const Center(child: CircularProgressIndicator(color: Colors.white))
            : Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Greeting and Logout
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Welcome, $teacherName',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                ElevatedButton(
                  onPressed: _logout,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white24,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20),
                    ),
                  ),
                  child: const Text('Logout', style: TextStyle(color: Colors.white)),
                ),
              ],
            ),
            const SizedBox(height: 40),
            const Center(
              child: Text(
                'Subjects You Teach',
                style: TextStyle(fontSize: 22, color: Colors.white, fontWeight: FontWeight.bold),
              ),
            ),
            const SizedBox(height: 20),
            Expanded(
              child: subjects.isEmpty
                  ? const Center(
                child: Text('No subjects assigned', style: TextStyle(color: Colors.white)),
              )
                  : ListView.builder(
                itemCount: subjects.length,
                itemBuilder: (context, index) {
                  return Card(
                    color: Colors.white24,
                    margin: const EdgeInsets.symmetric(vertical: 8),
                    child: ListTile(
                      title: Text(
                        subjects[index],
                        style: const TextStyle(color: Colors.white),
                      ),
                      trailing: const Icon(Icons.arrow_forward_ios, color: Colors.white),
                      onTap: () => _goToSubjectUploadPage(subjects[index]),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
