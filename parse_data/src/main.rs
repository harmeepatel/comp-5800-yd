#![allow(dead_code, unused)]

use serde_json::Value;

struct Config {
    jsonl_path: String,
    input: String,
    output: String,
}
impl Config {
    fn build(args: &mut Vec<String>) -> Result<Self, &'static str> {
        Ok(Config {
            jsonl_path: match args.get(1) {
                Some(q) => q.to_owned(),
                None => return Err("Provide a path to jsonl file."),
            },
            input: match args.get(2) {
                Some(fp) => fp.to_owned(),
                None => return Err("Provide a path to save source file."),
            },
            output: match args.get(3) {
                Some(fp) => fp.to_owned(),
                None => return Err("Provide a path to save target file."),
            },
        })
    }
}

fn main() {
    let config =
        Config::build(&mut std::env::args().collect::<Vec<String>>()).unwrap_or_else(|e| {
            eprintln!("{}", e);
            std::process::exit(1);
        });
    let file_content = std::fs::read_to_string(&config.jsonl_path).unwrap_or_else(|e| {
        eprintln!("{}", e);
        std::process::exit(1);
    });

    let mut json_lines: Vec<Value> = Vec::with_capacity(file_content.len());
    for line in file_content.lines() {
        json_lines.push(serde_json::from_str(line).unwrap_or_else(|e| {
            eprintln!("Something went wrong converting to json with error:\n{}", e);
            std::process::exit(1);
        }));
    }

    let src = parse_text(&json_lines, false);
    let tar = parse_text(&json_lines, true);

    let mut new_src: Vec<&str> = Vec::with_capacity(src.len());
    let mut new_tar: Vec<&str> = Vec::with_capacity(tar.len());

    for i in 0..src.len() {
        if !src[i].eq(&tar[i]) {
            new_src.push(&src[i]);
            new_tar.push(&tar[i]);
        }
    }
    // let new_src = src;
    // let new_tar = tar;

    println!("src len: {}", &new_src.len());
    println!("src len: {}", &new_tar.len());

    if let Err(e) = save_file(&config.input, &new_src) {
        eprintln!("err: {}", e);
        std::process::exit(1);
    }
    if let Err(e) = save_file(&config.output, &new_tar) {
        eprintln!("err: {}", e);
        std::process::exit(1);
    }
}

fn save_file(path: &str, data: &Vec<&str>) -> Result<(), String> {
    let data = data.join("\n");

    let path = match std::env::current_dir() {
        Ok(cur_dir) => {
            let cur_dir = cur_dir.join(path);
            cur_dir
                .to_str()
                .unwrap_or_else(|| {
                    eprintln!("Problem converting PathBuf to str");
                    std::process::exit(1);
                })
                .to_owned()
        }
        Err(e) => return Err(format!("Problem reading current dir with error:\n{}", e)),
    };

    match std::fs::write(&path, data) {
        Ok(_) => {
            println!("Written to {}", &path);
        }
        Err(e) => {
            return Err(format!(
                "Problem writing to file: {}, with error:\n{}",
                &path, e
            ))
        }
    };

    Ok(())
}

fn save_file_tab_separated(
    path: &str,
    source: &Vec<&str>,
    target: &Vec<&str>,
) -> Result<(), &'static str> {
    let mut data: Vec<String> = Vec::new();
    for i in 0..source.len() {
        let st_pair = [source[i], target[i]];
        let tmp_str = st_pair.join("\t");
        data.push(tmp_str);
    }
    let data = data.join("\n");

    let path = match std::env::current_dir() {
        Ok(cur_dir) => {
            let cur_dir = cur_dir.join(path);
            cur_dir
                .to_str()
                .unwrap_or_else(|| {
                    eprintln!("Problem converting PathBuf to str");
                    std::process::exit(1);
                })
                .to_owned()
        }
        Err(_) => return Err("Problem reading current dir"),
    };
    match std::fs::write(&path, data) {
        Ok(_) => {
            println!("Written to {}", &path);
        }
        Err(_) => return Err("Problem writing to file"),
    };

    Ok(())
}

fn parse_text(obj_vec: &Vec<Value>, is_target: bool) -> Vec<String> {
    let special_chars = [
        "!", "\"", "#", "$", "%", "&", "'", "(", ")", "*", "+", ",", "-", ".", "/", ":", ";", "<",
        "=", ">", "?", "@", "[", "\\", "]", "^", "_", "`", "{", "|", "}", "~",
    ];

    let from = if is_target { "tgt" } else { "src" };
    let mut lines: Vec<String> = Vec::new();

    for val in obj_vec.iter() {
        let edits = val["edits"].as_array().unwrap_or_else(|| {
            eprintln!("Something went wrong parsing to array.");
            std::process::exit(1);
        });
        let last_edit = &edits[edits.len() - 1];

        if !last_edit["is_typo"].as_bool().unwrap_or(false)
            || last_edit[from]["lang"].as_str().unwrap_or("") != "eng"
        {
            continue;
        }

        let mut text = last_edit[from]["text"]
            .as_str()
            .unwrap_or_else(|| {
                eprintln!("Something went wrong parsing to string.");
                std::process::exit(1);
            })
            .to_string();

        for c in special_chars {
            text = text.replace(c, " ");
        }

        text = text
            .trim()
            .to_lowercase()
            .split(' ')
            .collect::<Vec<_>>()
            .iter()
            .filter_map(|word| match word.is_empty() {
                true => None,
                false => Some(*word),
            })
            .collect::<Vec<_>>()
            .join(" ");

        for word in text.split(' ') {
            if word.starts_with("0x") {
                println!("from {}: {}", &from, &text);
                println!();
                continue;
            }
        }

        lines.push(text);
    }

    lines
}
