CC = gcc
CXX = g++
CFLAGS = -Wall -Wextra -O2
CXXFLAGS = -Wall -Wextra -O2 -std=c++11

RELEASE_CFLAGS = -O3 -DNDEBUG -s
RELEASE_CXXFLAGS = -O3 -DNDEBUG -s
DEBUG_CFLAGS = -g -DDEBUG
DEBUG_CXXFLAGS = -g -DDEBUG

TARGET = infer

SRCS = main.cpp

OBJS = $(SRCS:.cpp=.o)
.PHONY: all clean release debug

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^

release: CFLAGS += $(RELEASE_CFLAGS)
release: CXXFLAGS += $(RELEASE_CXXFLAGS)

release: clean $(TARGET)

debug: CFLAGS += $(DEBUG_CFLAGS)
debug: CXXFLAGS += $(DEBUG_CXXFLAGS)

debug: clean $(TARGET)

clean:
	rm -f $(OBJS) $(TARGET)