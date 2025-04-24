import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:shared_preferences/shared_preferences.dart';

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
  bool rememberMe = false;

  @override
  void initState() {
    super.initState();
    loadSavedCredentials();
  }

  Future<void> loadSavedCredentials() async {
    final prefs = await SharedPreferences.getInstance();
    final savedEmail = prefs.getString('saved_email');
    final savedPassword = prefs.getString('saved_password');
    final savedRememberMe = prefs.getBool('remember_me') ?? false;

    if (savedRememberMe && savedEmail != null && savedPassword != null) {
      setState(() {
        emailController.text = savedEmail;
        passwordController.text = savedPassword;
        rememberMe = true;
      });

      // Delay to ensure widget builds before login attempt
      Future.delayed(const Duration(milliseconds: 300), () {
        loginTeacher();
      });
    }
  }

  Future<void> loginTeacher() async {
    final serverUrl = dotenv.env['SERVER_URL'] ?? '';
    String email = emailController.text.trim();
    String password = passwordController.text;

    if (!email.endsWith('@rgipt.ac.in')) {
      setState(() {
        errorMessage = 'Please enter a valid RGIPT email address.';
      });
      return;
    }

    setState(() => isLoading = true);

    try {
      var response = await http.post(
        Uri.parse('$serverUrl/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'email': email, 'password': password}),
      );

      final data = json.decode(response.body);
      if (response.statusCode == 200 && data['success']) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('teacher_id', data['teacher']['id'].toString());

        if (rememberMe) {
          await prefs.setString('saved_email', email);
          await prefs.setString('saved_password', password);
          await prefs.setBool('remember_me', true);
        } else {
          await prefs.remove('saved_email');
          await prefs.remove('saved_password');
          await prefs.setBool('remember_me', false);
        }

        if (mounted) {
          Navigator.pushReplacementNamed(context, '/dashboard');
        }
      } else {
        setState(() {
          errorMessage = data['message'] ?? 'Login failed. Please try again.';
        });
      }
    } catch (e) {
      setState(() {
        errorMessage = 'Error: $e';
      });
    } finally {
      setState(() => isLoading = false);
    }
  }

  InputDecoration customInputDecoration(String label) {
    return InputDecoration(
      labelText: label,
      filled: true,
      fillColor: Colors.white,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
    );
  }

  @override
  Widget build(BuildContext context) {
    final themeColor = Colors.blueAccent;
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;

    return Scaffold(
      backgroundColor: themeColor.shade100,
      body: Center(
        child: SingleChildScrollView(
          padding: EdgeInsets.symmetric(
            horizontal: screenWidth * 0.06,
            vertical: screenHeight * 0.04,
          ),
          child: Container(
            padding: EdgeInsets.all(screenWidth * 0.06),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: themeColor.withOpacity(0.3),
                  blurRadius: 20,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.lock_outline, size: screenWidth * 0.15, color: themeColor),
                const SizedBox(height: 12),
                Text(
                  'Teacher Login',
                  style: TextStyle(
                    fontSize: screenWidth * 0.06,
                    fontWeight: FontWeight.bold,
                    color: themeColor.shade700,
                  ),
                ),
                const SizedBox(height: 24),
                TextField(
                  controller: emailController,
                  decoration: customInputDecoration("College Email"),
                  keyboardType: TextInputType.emailAddress,
                ),
                const SizedBox(height: 20),
                TextField(
                  controller: passwordController,
                  decoration: customInputDecoration("Password"),
                  obscureText: true,
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    InkWell(
                      onTap: () {
                        setState(() {
                          rememberMe = !rememberMe;
                        });
                      },
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Checkbox(
                            value: rememberMe,
                            onChanged: (value) {
                              setState(() {
                                rememberMe = value ?? false;
                              });
                            },
                          ),
                          const Text("Remember Me"),
                        ],
                      ),
                    ),
                    const Spacer(),
                    TextButton(
                      onPressed: () => Navigator.pushNamed(context, '/forgot-password'),
                      child: const Text("Forgot Password?"),
                    ),
                  ],
                ),
                if (errorMessage.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 8.0),
                    child: Text(
                      errorMessage,
                      style: TextStyle(color: Colors.red.shade700, fontSize: 14),
                      textAlign: TextAlign.center,
                    ),
                  ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: isLoading ? null : loginTeacher,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: themeColor,
                      padding: EdgeInsets.symmetric(vertical: screenHeight * 0.02),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: isLoading
                        ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        color: Colors.white,
                        strokeWidth: 2,
                      ),
                    )
                        : const Text("Login", style: TextStyle(fontSize: 16)),
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
