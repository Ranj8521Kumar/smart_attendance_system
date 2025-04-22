import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';  // For encoding data to JSON

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  String errorMessage = '';
  bool isLoading = false;

  // Function to login the teacher
  Future<void> loginTeacher() async {
    String email = emailController.text;
    String password = passwordController.text;

    // Check if the email ends with '@rgipt.ac.in'
    if (!email.endsWith('@rgipt.ac.in')) {
      setState(() {
        errorMessage = 'Please enter a valid RGIPT email address.';
      });
      return;
    }

    setState(() {
      isLoading = true;
    });

    // Backend URL for login verification
    var url = Uri.parse('http://192.168.31.223:5000/login');  // Replace with your backend URL

    try {
      var response = await http.post(
        url,
        body: json.encode({
          'email': email,
          'password': password,
        }),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      // Check if the login was successful
      if (response.statusCode == 200) {
        // Parse the response from backend (assuming JSON response)
        var data = json.decode(response.body);
        if (data['success']) {
          final prefs = await SharedPreferences.getInstance();
          String teacherId = data['teacher']['id'].toString();

          // Debug print
          print('Received teacher ID from backend: $teacherId');

          await prefs.setString('teacher_id', teacherId);

          // Navigate to the next page (dashboard or home)
          Navigator.pushReplacementNamed(context, '/dashboard');
        } else {
          // Show error message if login fails
          setState(() {
            errorMessage = data['message'] ?? 'Login failed. Please check your credentials.';
          });
        }
      } else {
        setState(() {
          errorMessage = 'Error: ${response.statusCode}. Please try again.';
        });
      }
    } catch (e) {
      setState(() {
        errorMessage = 'Error: $e. Please try again.';
      });
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  InputDecoration boxedDecoration(String label) {
    return InputDecoration(
      labelText: label,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Teacher Login")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 24),
            TextField(
              controller: emailController,
              decoration: boxedDecoration("College Email"),
              keyboardType: TextInputType.emailAddress,
            ),
            const SizedBox(height: 20),
            TextField(
              controller: passwordController,
              decoration: boxedDecoration("Password"),
              obscureText: true,
            ),
            const SizedBox(height: 10),
            Align(
              alignment: Alignment.centerRight,
              child: TextButton(
                onPressed: () {
                  Navigator.pushNamed(context, '/forgot-password');
                },
                child: const Text("Forgot Password?"),
              ),
            ),
            const SizedBox(height: 20),
            if (errorMessage.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(bottom: 16.0),
                child: Text(
                  errorMessage,
                  style: const TextStyle(color: Colors.red, fontSize: 14),
                ),
              ),
            isLoading
                ? const Center(child: CircularProgressIndicator())
                : ElevatedButton(
                    onPressed: loginTeacher,
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: const Text("Login"),
                  ),
          ],
        ),
      ),
    );
  }
}
