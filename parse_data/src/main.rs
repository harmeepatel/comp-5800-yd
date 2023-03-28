use std::io::Result;

use serde_json::Value;

fn parse_text(lines: &Vec<Value>, is_target: bool) -> Vec<&str> {
    let from = if is_target { "tgt" } else { "src" };

    lines
        .iter()
        .map(|line| {
            line["edits"]
                .as_array()
                .unwrap_or_else(|| {
                    eprintln!("Something went wrong with error parsing to array.");
                    std::process::exit(1);
                })
                .iter()
                .filter_map(|e| {
                    if e["is_typo"].as_bool().unwrap_or(true) {
                        Some(
                            e[from]["text"]
                                .as_str()
                                .unwrap_or_else(|| {
                                    eprintln!("Something went wrong with error parsing to string.");
                                    std::process::exit(1);
                                })
                                .trim(),
                        )
                    } else {
                        None
                    }
                })
                .collect::<Vec<_>>()
        })
        .flatten()
        .collect()
}

fn save_file(path: &str, data: &Vec<&str>) -> Result<()> {
    let data = data.join("\n");
    let path = std::env::current_dir()
        .unwrap_or_else(|e| {
            eprintln!("Problem reading current dir with error {}", e);
            std::process::exit(1);
        })
        .join(path);
    if let Err(e) = std::fs::write(&path, data) {
        eprintln!("Problem writing to file with error {}", e);
        std::process::exit(1);
    }
    println!(
        "Written to {}",
        &path.to_str().unwrap_or_else(|| {
            eprintln!("Problem converting Path to str.");
            std::process::exit(1);
        })
    );
    Ok(())
}

fn main() {
    let path = std::env::args().nth(1).unwrap_or_else(|| {
        eprintln!("Please provide path to jsonl file.");
        std::process::exit(1);
    });
    let file_content = std::fs::read_to_string(&path).unwrap_or_else(|e| {
        eprintln!("Something went wrong with error {}", e);
        std::process::exit(1);
    });

    let mut json_lines: Vec<Value> = vec![];
    for line in file_content.lines() {
        json_lines.push(serde_json::from_str(line).unwrap_or_else(|e| {
            eprintln!("Something went wrong converting to json with error {}", e);
            std::process::exit(1);
        }));
    }

    let src = parse_text(&json_lines, false);
    let target = parse_text(&json_lines, true);

    if let Err(e) = save_file("../data/github-typo-corpus-source.txt", &src) {
        eprintln!(
            "Someting went wrong saving data to {}, with error{}",
            "../data/github-typo-corpus-source.txt", e
        );
        std::process::exit(1);
    }
    if let Err(e) = save_file("../data/github-typo-corpus-target.txt", &target) {
        eprintln!(
            "Someting went wrong saving data to {}, with error{}",
            "../data/github-typo-corpus-source.txt", e
        );
        std::process::exit(1);
    }
}
