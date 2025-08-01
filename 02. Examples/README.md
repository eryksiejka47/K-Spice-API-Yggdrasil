# Code and Use Cases

The purpose of this project is to provide users with a simple way to interact with large models in K-Spice by leveraging the K-Spice API.
The focus was on making the code modular and easy to understand. To achieve this, the interaction logic was divided into three main components: Gathering, Processing, and Display, as illustrated in the figure below.

![cmd](https://github.com/eryksiejka47/K-Spice-API-Yggdrasil/blob/c584befc03935a049bdc69743a5abc52bcdd02fb/images/Block_Diagram.PNG)


### Gathering:

The code in the "Gathering" module is responsible for generating the CSV files that will later be processed and used for data visualization.
Users can program their own test sequences — for example, changing the opening of a valve or adjusting a setpoint in a controller.

By using a switch-case structure, it’s possible to run multiple sequences in succession. This is done by saving the data, reloading the initial conditions, and then executing a new test.
Such a setup is especially beneficial for large models like Yggdrasil, where simulation speed is low.

A smart strategy might be to schedule predefined test sequences to run overnight in order to save time.

---


### Processing:
K-Spice offers a wide range of parameters that can be logged and used for custom analysis.
In most cases, no additional data processing is required — the raw output is sufficient.

However, there are situations where custom calculations on the CSV files are necessary before plotting.
For example, calculating the pressure difference between two points or performing other derived measurements.

---

### Display
After completing the tests, it’s important to present the data in a clear and meaningful way.
As part of this project, code was developed to generate plots in both PNG and HTML formats.
