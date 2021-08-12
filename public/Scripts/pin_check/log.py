import sys

class Logging:
    total_test = 0
    total_pass = 0
    total_fail = 0
    def message(msg_type, msg):
        f = open("process.log", "a")
        if msg_type == "INFO":
            print("INFO: %s" % (msg))
            f.write("INFO: %s\n" % (msg))

        elif msg_type == "PASS":
            Logging.total_test += 1
            Logging.total_pass += 1
            print("    PASS: %s" % (msg))
            f.write("    PASS: %s\n" % (msg))
        elif msg_type == "FAIL":
            Logging.total_test += 1
            Logging.total_fail += 1
            print("    FAIL: %s" % (msg))
            f.write("    FAIL: %s\n" % (msg))
        elif msg_type == "RESULT":
            print("        %s" % (msg))
            f.write("        %s\n" % (msg))
        elif msg_type == "WARNING":
            print("WARNING: %s" % (msg))
            f.write("WARNING: %s\n" % (msg))
        elif msg_type == "ERROR":
            print("ERROR: %s" % (msg))
            f.write("ERROR: %s\n" % (msg))
            sys.exit()
        elif msg_type == "EXTRA":
            print("    %s" % (msg))
            f.write("    %s\n" % (msg))


    def summary():
        print('Summary: Total Tests: %s, Total Passed: %s, Total Failure: %s' %
              (Logging.total_test, Logging.total_pass, Logging.total_fail))
        f = open("process.log", "a")
        f.write('Summary: Total Tests: %s, Total Passed: %s, Total Failure: %s\n' %
                (Logging.total_test, Logging.total_pass, Logging.total_fail))
        if Logging.total_test == Logging.total_pass or Logging.total_test == 0:
            result = "SUCCESS"
        else:
            result = "FAILURE"
        print("#############\n"
              "## %s ##\n"
              "#############" % result)
        f.write("#############\n"
                "## %s ##\n"
                "#############" % result)
