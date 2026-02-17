using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;

namespace LogicService
{
    // Модель данных для десериализации JSON от Python
    public class CalcRequest
    {
        public string num1 { get; set; }
        public string num2 { get; set; }
        public string operation { get; set; }
    }

    class Program
    {
        static void Main(string[] args)
        {
            TcpListener server = new TcpListener(IPAddress.Parse("127.0.0.1"), 5000);
            server.Start();
            Console.WriteLine("Ожидание клиента...");

            while (true)
            {
                using TcpClient client = server.AcceptTcpClient();
                Console.WriteLine("Клиент подключен!");

                using NetworkStream stream = client.GetStream();
                byte[] buffer = new byte[1024];

                try
                {
                    while (true)
                    {
                        int bytesRead = stream.Read(buffer, 0, buffer.Length);
                        if (bytesRead == 0) break; // Клиент отключился

                        string jsonData = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                        Console.WriteLine($"Получено: {jsonData}");

                        // Парсим JSON и считаем
                        var request = JsonSerializer.Deserialize<CalcRequest>(jsonData);
                        string result = Calculate(request);

                        // Отправляем ответ обратно
                        byte[] responseData = Encoding.UTF8.GetBytes(result);
                        stream.Write(responseData, 0, responseData.Length);
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Ошибка: {ex.Message}");
                }
                Console.WriteLine("Клиент отсоединился. Ждем нового подключения...");
            }
        }

        static string Calculate(CalcRequest req)
        {
            if (!double.TryParse(req.num1, out double a) || !double.TryParse(req.num2, out double b))
                return "Ошибка: Не числа";

            return req.operation switch
            {
                "+" => (a + b).ToString(),
                "-" => (a - b).ToString(),
                "*" => (a * b).ToString(),
                "/" => b != 0 ? (a / b).ToString() : "Деление на 0!",
                _ => "Неизвестная операция"
            };
        }
    }
}
