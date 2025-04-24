import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';

class ForgotPasswordScreen extends StatelessWidget {
  final TextEditingController emailController = TextEditingController();

  ForgotPasswordScreen({super.key});

  void handleResetPassword(BuildContext context) async {
    final serverUrl = dotenv.env['SERVER_URL'] ?? '';
    final email = emailController.text.trim();

    if (!email.endsWith('@rgipt.ac.in')) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a valid @rgipt.ac.in email')),
      );
      return;
    }

    final url = Uri.parse('$serverUrl/forgot-password');

    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email}),
      );

      final responseData = jsonDecode(response.body);

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(responseData['message'] ?? 'Success')),
        );

        // Redirect after 2 seconds
        Future.delayed(const Duration(seconds: 2), () {
          Navigator.pushReplacementNamed(context, '/login'); // Replace with your login route
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(responseData['message'] ?? 'Failed')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Error connecting to server")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.blueAccent.shade100,
      appBar: AppBar(
        title: const Text("Forgot Password"),
        backgroundColor: Colors.white,
        foregroundColor: Colors.blueAccent,
        elevation: 0,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            elevation: 8,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 30.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Text(
                    "Enter your registered college email to reset your password.",
                    style: TextStyle(fontSize: 16),
                  ),
                  const SizedBox(height: 20),
                  TextField(
                    controller: emailController,
                    keyboardType: TextInputType.emailAddress,
                    decoration: InputDecoration(
                      labelText: "College Email",
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                  ),
                  const SizedBox(height: 30),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blueAccent.shade100,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                    onPressed: () => handleResetPassword(context),
                    child: const Text("Send Reset Link"),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
