import 'package:flutter/material.dart';
import 'upload_image.dart';
import 'todays_attendance_page.dart';

enum SubjectPageOption { upload, attendance }

class SubjectUploadPage extends StatefulWidget {
  final String subjectCode;
  final String subjectName;

  const SubjectUploadPage({
    Key? key,
    required this.subjectCode,
    required this.subjectName,
  }) : super(key: key);

  @override
  State<SubjectUploadPage> createState() => _SubjectUploadPageState();
}

class _SubjectUploadPageState extends State<SubjectUploadPage> {
  SubjectPageOption selectedOption = SubjectPageOption.upload;

  // Function to toggle the selected option when the text is clicked
  void toggleOption(SubjectPageOption option) {
    setState(() {
      selectedOption = option;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            Navigator.pop(context);
          },
        ),
        backgroundColor: Colors.blue, // Customize if necessary
        elevation: 0, // Remove shadow if you don't want it
      ),
      body: Column(
        children: [
          // Display the subject name in the body
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 16),
            child: Center(
              child: Text(
                '${widget.subjectName} (${widget.subjectCode})',
                style: TextStyle(
                  fontSize: 25,
                  fontWeight: FontWeight.w600,
                  color: Colors.black87,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),

          // Radio Buttons for toggling pages
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              GestureDetector(
                onTap: () => toggleOption(SubjectPageOption.upload),
                child: Row(
                  children: [
                    Radio<SubjectPageOption>(
                      value: SubjectPageOption.upload,
                      groupValue: selectedOption,
                      onChanged: (value) {
                        setState(() {
                          selectedOption = value!;
                        });
                      },
                    ),
                    const Text("Upload Images"),
                  ],
                ),
              ),
              const SizedBox(width: 20),
              GestureDetector(
                onTap: () => toggleOption(SubjectPageOption.attendance),
                child: Row(
                  children: [
                    Radio<SubjectPageOption>(
                      value: SubjectPageOption.attendance,
                      groupValue: selectedOption,
                      onChanged: (value) {
                        setState(() {
                          selectedOption = value!;
                        });
                      },
                    ),
                    const Text("Today's Attendance"),
                  ],
                ),
              ),
            ],
          ),
          const Divider(thickness: 1),
          Expanded(
            child: selectedOption == SubjectPageOption.upload
                ? ImageUploadPage(
              subjectCode: widget.subjectCode,
              subjectName: widget.subjectName,
            )
                : TodaysAttendancePage(
              subjectCode: widget.subjectCode,
              subjectName: widget.subjectName,
            ),
          ),
        ],
      ),
    );
  }
}
