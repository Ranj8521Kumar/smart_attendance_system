import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';

class AttendanceTablePage extends StatefulWidget {
  final String subjectCode;
  final String subjectName;

  const AttendanceTablePage({
    Key? key,
    required this.subjectCode,
    required this.subjectName,
  }) : super(key: key);

  @override
  _AttendanceTablePageState createState() => _AttendanceTablePageState();
}

class _AttendanceTablePageState extends State<AttendanceTablePage> {
  List<Map<String, dynamic>> attendanceData = [];
  List<String> dates = [];
  bool isLoading = false;
  String? errorMessage;

  @override
  void initState() {
    super.initState();
    SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
      DeviceOrientation.landscapeLeft,
      DeviceOrientation.landscapeRight,
    ]);
    _fetchAttendanceData();
  }

  Future<void> _fetchAttendanceData() async {
    final serverUrl = dotenv.env['SERVER_URL'] ?? '';
    setState(() {
      isLoading = true;
      errorMessage = null;
      attendanceData = [];
      dates = [];
    });

    try {
      final response = await http.get(
        Uri.parse('$serverUrl/get_all_attendance?subject_code=${widget.subjectCode}'),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode != 200) {
        throw Exception('Server error: ${response.statusCode}');
      }

      final data = json.decode(response.body);
      if (data['success'] != true) {
        throw Exception(data['message'] ?? 'Failed to fetch attendance');
      }

      setState(() {
        attendanceData = List<Map<String, dynamic>>.from(data['attendance'] ?? []);
        dates = List<String>.from(data['dates'] ?? []); // Get the date vector from the response
      });
    } catch (e) {
      setState(() {
        errorMessage = e.toString();
      });
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  Widget _buildAttendanceTable() {
    // Fixed column widths
    const double srNoWidth = 80.0;  // Fixed width for Sr. No.
    const double rollNoWidth = 120.0; // Fixed width for Roll No.
    const double nameWidth = 200.0;  // Fixed width for Name
    const double percentageWidth = 100.0; // Fixed width for Percentage
    const double dateWidth = 80.0;  // Fixed width for each date column

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          widget.subjectName,
          style: const TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        attendanceData.isEmpty
            ? const Text(
          'No attendance records found.',
          style: TextStyle(fontSize: 18),
        )
            : Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Fixed Columns (Sr.No + Roll No)
            DataTable(
              headingRowHeight: 44,
              dataRowHeight: 44,
              columnSpacing: 0,
              columns: [
                _buildDataColumn('Sr. No.', srNoWidth),
                _buildDataColumn('Roll No.', rollNoWidth),
              ],
              rows: attendanceData.asMap().entries.map((entry) {
                return DataRow(
                  cells: [
                    _buildDataCell((entry.key + 1).toString(), srNoWidth),
                    _buildDataCell(entry.value['roll_number'] ?? '', rollNoWidth),
                  ],
                );
              }).toList(),
              border: TableBorder.all(color: Colors.grey),
            ),
            // Scrollable Columns (Name + Percentage + Dates)
            Expanded(
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: DataTable(
                  headingRowHeight: 44,
                  dataRowHeight: 44,
                  columnSpacing: 0,
                  columns: [
                    _buildDataColumn('Name', nameWidth),
                    _buildDataColumn('Percentage', percentageWidth),
                    ...dates.map((date) => _buildDataColumn(date, dateWidth, fontSize: 10)),
                  ],
                  rows: attendanceData.map((student) {
                    final totalClasses = student['attendance'].length;
                    final attendedClasses = student['attendance'].where((s) => s == 1).length;
                    final percentage = totalClasses == 0
                        ? 0
                        : (attendedClasses / totalClasses) * 100;

                    return DataRow(
                      cells: [
                        _buildDataCell(student['name'] ?? '', nameWidth),
                        _buildDataCell('${percentage.toStringAsFixed(2)}%', percentageWidth),
                        ...dates.map((date) {
                          final dateIndex = dates.indexOf(date);
                          final status = (dateIndex < student['attendance'].length)
                              ? student['attendance'][dateIndex]
                              : 0;
                          return _buildStatusCell(status, dateWidth);
                        }).toList(),
                      ],
                    );
                  }).toList(),
                  border: TableBorder.all(color: Colors.grey),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  // Helper methods for reusable components
  DataColumn _buildDataColumn(String text, double width, {double fontSize = 12}) {
    return DataColumn(
      label: SizedBox(
        width: width,
        child: Center(
          child: Text(
            text,
            style: TextStyle(fontSize: fontSize),
          ),
        ),
      ),
    );
  }

  DataCell _buildDataCell(String text, double width, {double fontSize = 12}) {
    return DataCell(
      SizedBox(
        width: width,
        child: Center(
          child: Text(
            text,
            style: TextStyle(fontSize: fontSize),
          ),
        ),
      ),
    );
  }

  DataCell _buildStatusCell(int status, double width) {
    return DataCell(
      SizedBox(
        width: width,
        child: Center(
          child: Text(
            status == 1 ? '1' : '0',
            style: TextStyle(
              fontSize: 12,
              color: status == 1 ? Colors.green : Colors.red,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Attendance Table'),
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : errorMessage != null
          ? Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Text(
            errorMessage!,
            style: const TextStyle(
              fontSize: 20,
              color: Colors.red,
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
          ),
        ),
      )
          : Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(child: _buildAttendanceTable()),
      ),
    );
  }
}
