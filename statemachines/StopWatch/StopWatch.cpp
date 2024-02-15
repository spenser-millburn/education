#include <chrono>
#include <iostream>
#include <thread>

enum class State { Stopped, Running, Paused };

class Stopwatch {
public:
    void start() {
    currentState = State::Running;
    startTime = std::chrono::steady_clock::now();
    std::cout << "Stopwatch started." << std::endl;
  }

  void pause() {
    if (currentState == State::Running) {
      currentState = State::Paused;
      pauseTime = std::chrono::steady_clock::now();
      std::cout << "Stopwatch paused." << std::endl;
    } else {
      std::cout << "Stopwatch is not running." << std::endl;
    }
  }

  void resume() {
    if (currentState == State::Paused) {
      currentState = State::Running;
      auto pauseDuration = std::chrono::steady_clock::now() - pauseTime;
      startTime += pauseDuration;
      std::cout << "Stopwatch resumed." << std::endl;
    } else {
      std::cout << "Stopwatch is not paused." << std::endl;
    }
  }

  void stop() {
    if (currentState != State::Stopped) {
      currentState = State::Stopped;
      std::cout << "Stopwatch stopped." << std::endl;
    } else {
      std::cout << "Stopwatch is already stopped." << std::endl;
    }
  }

  void displayElapsedTime() {
    if (currentState == State::Running) {
      auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(
          std::chrono::steady_clock::now() - startTime);
      std::cout << "Elapsed time: " << elapsed.count() << "s" << std::endl;
    } else {
      std::cout << "Stopwatch is not running." << std::endl;
    }
  }

private:
  State currentState = State::Stopped;
  std::chrono::time_point<std::chrono::steady_clock> startTime;
  std::chrono::time_point<std::chrono::steady_clock> pauseTime;
};

int main() {
  Stopwatch stopwatch;
  stopwatch.start();
  std::this_thread::sleep_for(std::chrono::seconds(2));
  stopwatch.pause();
  std::this_thread::sleep_for(std::chrono::seconds(1));                                                                                                                         
  stopwatch.resume();                                                                                                                                                           
  std::this_thread::sleep_for(std::chrono::seconds(3));                                                                                                                         
  stopwatch.displayElapsedTime();                                                                                                                                               
  stopwatch.stop();                                                                                                                                                             
   return 0;                                                                                                                                                                     
 }                   
