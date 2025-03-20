#![no_std]
#![no_main]

use defmt::info;
use esp_hal::{
    clock::CpuClock,
    delay::Delay,
    gpio::{Level, Output, OutputConfig},
    main,
    peripherals::Peripherals,
    rmt::{PulseCode, Rmt},
    time::{Duration, Instant, Rate},
};

#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    loop {}
}

extern crate alloc;

#[main]
fn main() -> ! {
    // generator version: 0.3.1

    rtt_target::rtt_init_defmt!();

    let config = esp_hal::Config::default().with_cpu_clock(CpuClock::max());
    let peripherals = esp_hal::init(config);

    // Обычный светодиод на GPIO22
    let mut led = Output::new(peripherals.GPIO22, Level::High, OutputConfig::default());

    // Инициализация кучи для динамической памяти
    esp_alloc::heap_allocator!(size: 72 * 1024);

    // Создание объекта Delay для точных задержек
    let delay = Delay::new();

    // Настройка RMT для управления RGB-светодиодом на GPIO8
    let freq = Rate::from_mhz(80);
    let rmt = Rmt::new(peripherals.RMT, freq);

    // Определение сигналов для WS2812 (время в наносекундах)
    let t0h = PulseCode::new(Level::High, 400, Level::Low, 850); // Логический 0: 400 нс high, 850 нс low
    let t1h = PulseCode::new(Level::High, 800, Level::Low, 450); // Логический 1: 800 нс high, 450 нс low
    let reset = PulseCode::new(Level::High, 0, Level::Low, 50_000); // Сброс: 0 нс high, 50 мкс low

    // Массив для одного RGB-светодиода: 24 бита + сброс
    // let mut rgb_data = [PulseCode::default(); 25];

    loop {
        info!("Hello world!");
        let delay_start = Instant::now();
        while delay_start.elapsed() < Duration::from_millis(500) {}
    }

    // for inspiration have a look at the examples at https://github.com/esp-rs/esp-hal/tree/esp-hal-v1.0.0-beta.0/examples/src/bin
}
