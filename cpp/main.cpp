#include "iostream"
#include "chrono"
#include "thread"
#include "cstdint"
#include "time.h"
#include "cstring"
#include "string"
#include "vector"
#include "map"

namespace logger {
    typedef enum {
        DEBUG,
        INFO,
        WARN,
        ERROR
    } LogLevel;

    void log(LogLevel level, const std::string &message) {
        const char* levelStr;
        switch (level) {
            case DEBUG: levelStr = "DEBUG"; break;
            case INFO:  levelStr = "INFO";  break;
            case WARN:  levelStr = "WARN";  break;
            case ERROR: levelStr = "ERROR"; break;
            default:    levelStr = "UNKNOWN"; break;
        }

        time_t now = time(0);
        char* dt = ctime(&now);
        dt[strlen(dt)-1] = '\0'; // Remove newline character

        std::cout << "[" << dt << "] [" << levelStr << "] " << message << std::endl;
    }

    void info(const std::string &message) {
        log(INFO, message);
    }

    void debug(const std::string &message) {
        log(DEBUG, message);
    }

    void warn(const std::string &message) {
        log(WARN, message);
    }

    void error(const std::string &message) {
        log(ERROR, message);
    }
}

namespace options {
    class Options {
    public:
        std::map<std::string, std::string> args;

        std::string get(const std::string &key, const std::string &defaultValue="") const {
            auto it = args.find(key);
            if (it != args.end()) {
                return it->second;
            }
            return defaultValue;
        }

        std::string toString() const {
            std::string result;
            for (const auto &pair : args) {
                result += pair.first + ": " + pair.second + "\n";
            }
            return result;
        }

        void parseOpts(int argc, char** argv) {
            for (int i = 1; i < argc; i++) {
                std::string arg = argv[i];
                if (arg == "--help") {
                    help();
                    exit(0);
                } else if (arg.rfind("--", 0) == 0 && i + 1 < argc) {
                    std::string key = arg.substr(2);
                    std::string value = argv[++i];
                    args[key] = value;
                }
            }
        }

        void help() const {
            std::cout << "Usage: ./inference_app [options]\n";
            std::cout << "Options:\n";
            std::cout << "  --model <model_path>       Path to the model file\n";
            std::cout << "  --config <config_file>    Path to the config file\n";
            std::cout << "  --log_level <level>        Set log level (DEBUG, INFO, WARN, ERROR)\n";
            std::cout << "  --log <log_file>          Set log output file\n";
            std::cout << "  --help                     Show this help message\n";
        }

    };
}

int main(int argc, char** argv) {
    logger::info("Starting inference application...");
    options::Options opts;
    opts.parseOpts(argc, argv);
    logger::info("Using model: " + opts.get("model", "default_model_path"));
    logger::info("Using config: " + opts.get("config", "default_config_path"));
    logger::info("Log level: " + opts.get("log_level", "INFO"));


    logger::info("Init model done.");
    std::this_thread::sleep_for(std::chrono::seconds(1));

    logger::info("Start inference loop.");

    uint64_t counter = 0;
    while (true) {
        logger::info("Inference running... count: " + std::to_string(counter));
        counter++;
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
    return 0;
}